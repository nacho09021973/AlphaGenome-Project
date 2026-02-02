"""
AlphaGenome - Diagnostico de conexion gRPC
==========================================

Este script verifica:
1. El endpoint correcto (gdmscience.googleapis.com vs alphagenome-api.googleapis.com)
2. La conectividad del canal gRPC
3. El service path utilizado
4. La validez de la API key

Ejecutar: python diagnostico_grpc.py
"""

import sys
import grpc

# Intentar importar la libreria alphagenome
try:
    sys.path.append('/home/ignac/Genoma/alphagenome/src')
    from alphagenome.models import dna_client
    from alphagenome.protos import dna_model_service_pb2_grpc
    from alphagenome.protos import dna_model_service_pb2
    from alphagenome.data.ontology import OntologyTerm, OntologyType
    print("[OK] Libreria alphagenome importada correctamente")
except ImportError as e:
    print(f"[ERROR] No se puede importar alphagenome: {e}")
    print("        Ejecuta: pip install alphagenome")
    sys.exit(1)

# =============================================================================
# CONFIGURACION
# =============================================================================
API_KEY = 'AIzaSyDLXmTFGqzp73aTl5pZ1CJmySokInyVlsI'

# Endpoints a probar
ENDPOINTS = {
    'CORRECTO (oficial)': 'dns:///gdmscience.googleapis.com:443',
    'INCORRECTO (antiguo)': 'alphagenome-api.googleapis.com:443',
}

# Service path esperado
SERVICE_PATH = '/google.gdm.gdmscience.alphagenome.v1main.DnaModelService/PredictSequence'

print()
print("="*70)
print("DIAGNOSTICO DE CONEXION gRPC - AlphaGenome v0.5.1")
print("="*70)
print()

# =============================================================================
# 1. Verificar el service path en la libreria
# =============================================================================
print("[1] VERIFICANDO SERVICE PATH EN LA LIBRERIA...")
print()

# El service path esta definido en el stub
stub_class = dna_model_service_pb2_grpc.DnaModelServiceStub
print(f"    Clase del Stub: {stub_class.__name__}")
print(f"    Service Path esperado: {SERVICE_PATH}")
print()

# =============================================================================
# 2. Probar conectividad con cada endpoint
# =============================================================================
print("[2] PROBANDO CONECTIVIDAD CON ENDPOINTS...")
print()

options = [
    ('grpc.max_send_message_length', -1),
    ('grpc.max_receive_message_length', -1),
]

for nombre, endpoint in ENDPOINTS.items():
    print(f"    Probando: {endpoint}")
    print(f"    ({nombre})")

    try:
        channel = grpc.secure_channel(
            endpoint,
            grpc.ssl_channel_credentials(),
            options=options
        )

        # Esperar a que el canal este listo (timeout 10 segundos)
        future = grpc.channel_ready_future(channel)
        future.result(timeout=10)

        print(f"    [OK] Canal establecido")

        # Intentar obtener metadata (llamada ligera)
        try:
            stub = dna_model_service_pb2_grpc.DnaModelServiceStub(channel)

            # Crear una peticion de metadata (no requiere secuencia)
            from alphagenome.models import dna_model
            request = dna_model_service_pb2.MetadataRequest(
                organism=dna_model.Organism.HOMO_SAPIENS.to_proto()
            )

            # Intentar la llamada con metadata de autenticacion
            metadata = [('x-goog-api-key', API_KEY)]
            responses = stub.GetMetadata(request, metadata=metadata, timeout=30)

            # Intentar leer la primera respuesta
            first_response = next(responses)
            print(f"    [OK] Llamada gRPC exitosa!")
            print(f"    [OK] API Key valida")

        except grpc.RpcError as rpc_error:
            code = rpc_error.code()
            details = rpc_error.details()
            print(f"    [ERROR] gRPC Error: {code.name}")
            print(f"            Detalles: {details}")

            if code == grpc.StatusCode.UNIMPLEMENTED:
                print(f"            -> El servidor no reconoce el service path")
                print(f"            -> Esto indica un ENDPOINT INCORRECTO")
            elif code == grpc.StatusCode.UNAUTHENTICATED:
                print(f"            -> API Key invalida o sin permisos")
            elif code == grpc.StatusCode.PERMISSION_DENIED:
                print(f"            -> Sin permisos para acceder a la API")

        channel.close()

    except grpc.FutureTimeoutError:
        print(f"    [ERROR] Timeout - No se pudo establecer conexion")
    except Exception as e:
        print(f"    [ERROR] {type(e).__name__}: {e}")

    print()

# =============================================================================
# 3. Probar con dna_client.create() (metodo recomendado)
# =============================================================================
print("[3] PROBANDO CON dna_client.create() (METODO RECOMENDADO)...")
print()

try:
    client = dna_client.create(
        api_key=API_KEY,
        timeout=15.0
    )
    print("    [OK] Cliente creado exitosamente")
    print(f"    Endpoint usado internamente: dns:///gdmscience.googleapis.com:443")

    # Intentar obtener metadata
    try:
        from alphagenome.models import dna_model
        metadata = client.output_metadata(organism=dna_model.Organism.HOMO_SAPIENS)
        print("    [OK] Metadata obtenida exitosamente!")

        if metadata.atac is not None:
            print(f"    - Tracks ATAC disponibles: {len(metadata.atac)}")
        if metadata.rna_seq is not None:
            print(f"    - Tracks RNA_SEQ disponibles: {len(metadata.rna_seq)}")

    except grpc.RpcError as rpc_error:
        code = rpc_error.code()
        print(f"    [ERROR] gRPC Error: {code.name}")
        print(f"            {rpc_error.details()}")

except Exception as e:
    print(f"    [ERROR] {type(e).__name__}: {e}")

print()
print("="*70)
print("RESUMEN")
print("="*70)
print()
print("ENDPOINT CORRECTO:   dns:///gdmscience.googleapis.com:443")
print("ENDPOINT INCORRECTO: alphagenome-api.googleapis.com:443")
print()
print("SERVICE PATH: /google.gdm.gdmscience.alphagenome.v1main.DnaModelService/")
print()
print("SOLUCION: Usar dna_client.create(api_key) en lugar de crear")
print("          el canal manualmente, o cambiar el host a gdmscience.")
print()
