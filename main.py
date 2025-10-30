import paho.mqtt.client as mqtt
import ssl
import json
import time
import os
from datetime import datetime
import threading
from dotenv import load_dotenv

# Carregar variables d'entorn
load_dotenv(override=True)

# ============================================
# CONFIGURACIÓ DES DE .env
# ============================================

# Endpoint d'AWS IoT
AWS_IOT_ENDPOINT = os.getenv("AWS_IOT_ENDPOINT")

# Port (8883 per MQTT amb TLS)
AWS_IOT_PORT = int(os.getenv("AWS_IOT_PORT", "8883"))

# Paths dels certificats
PATH_TO_CERTIFICATE = os.getenv("PATH_TO_CERTIFICATE")
PATH_TO_PRIVATE_KEY = os.getenv("PATH_TO_PRIVATE_KEY")
PATH_TO_AMAZON_ROOT_CA = os.getenv("PATH_TO_AMAZON_ROOT_CA")

# Topics
SUBSCRIBE_TOPIC = os.getenv("SUBSCRIBE_TOPIC")
PUBLISH_TOPIC = os.getenv("PUBLISH_TOPIC")

# Interval de publicació (en segons)
PUBLISH_INTERVAL = int(os.getenv("PUBLISH_INTERVAL", "10"))

# Client ID (opcional, es pot personalitzar)
CLIENT_ID = os.getenv("CLIENT_ID", f"backend-python-{int(time.time())}")

# ============================================
# VALIDACIÓ DE CONFIGURACIÓ
# ============================================

def validate_config():
    """Valida que totes les variables necessàries estiguin configurades"""
    required_vars = {
        "AWS_IOT_ENDPOINT": AWS_IOT_ENDPOINT,
        "PATH_TO_CERTIFICATE": PATH_TO_CERTIFICATE,
        "PATH_TO_PRIVATE_KEY": PATH_TO_PRIVATE_KEY,
        "PATH_TO_AMAZON_ROOT_CA": PATH_TO_AMAZON_ROOT_CA,
        "SUBSCRIBE_TOPIC": SUBSCRIBE_TOPIC,
        "PUBLISH_TOPIC": PUBLISH_TOPIC
    }
    
    missing = [var for var, value in required_vars.items() if not value]
    
    if missing:
        print("ERROR: Falten les següents variables d'entorn:")
        for var in missing:
            print(f"  - {var}")
        return False
    
    # Validar que els fitxers de certificats existeixin
    cert_files = {
        "Certificate": PATH_TO_CERTIFICATE,
        "Private Key": PATH_TO_PRIVATE_KEY,
        "Root CA": PATH_TO_AMAZON_ROOT_CA
    }
    
    missing_files = [name for name, path in cert_files.items() if not os.path.isfile(path)]
    
    if missing_files:
        print("ERROR: No es troben els següents fitxers de certificats:")
        for name in missing_files:
            print(f"  - {name}: {cert_files[name]}")
        return False
    
    return True

# ============================================
# CALLBACKS
# ============================================

def on_connect(client, userdata, flags, rc):
    """Callback quan es connecta al broker"""
    if rc == 0:
        print(f"[{datetime.now()}] Connectat a AWS IoT amb èxit!")
        # Subscriure's al topic
        client.subscribe(SUBSCRIBE_TOPIC)
        print(f"[{datetime.now()}] Subscrit al topic: {SUBSCRIBE_TOPIC}")
    else:
        print(f"[{datetime.now()}] Error de connexió. Codi: {rc}")

def on_disconnect(client, userdata, rc):
    """Callback quan es desconnecta del broker"""
    if rc != 0:
        print(f"[{datetime.now()}] Desconnexió inesperada. Reconnectant...")

def on_message(client, userdata, msg):
    """Callback quan es rep un missatge"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now()}] Missatge rebut!")
    print(f"Topic: {msg.topic}")
    print(f"Payload: {msg.payload.decode('utf-8')}")
    print(f"{'='*60}\n")

def on_subscribe(client, userdata, mid, granted_qos):
    """Callback quan s'ha subscrit correctament"""
    print(f"[{datetime.now()}] Subscripció confirmada amb QoS: {granted_qos}")

def on_publish(client, userdata, mid):
    """Callback quan s'ha publicat un missatge"""
    print(f"[{datetime.now()}] Missatge publicat correctament (mid: {mid})")

# ============================================
# FUNCIÓ DE PUBLICACIÓ PERIÒDICA
# ============================================

def publish_periodic(client):
    """Publica missatges periòdicament al topic"""
    counter = 0
    while True:
        try:
            counter += 1
            message = {
                "message": f"Missatge automàtic #{counter}",
                "timestamp": datetime.now().isoformat(),
                "source": CLIENT_ID
            }
            
            result = client.publish(
                PUBLISH_TOPIC,
                payload=json.dumps(message),
                qos=1
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"[{datetime.now()}] Publicat missatge #{counter} al topic '{PUBLISH_TOPIC}'")
            else:
                print(f"[{datetime.now()}] Error en publicar missatge: {result.rc}")
            
            time.sleep(PUBLISH_INTERVAL)
            
        except Exception as e:
            print(f"[{datetime.now()}] Error en publicar: {e}")
            time.sleep(PUBLISH_INTERVAL)

# ============================================
# PROGRAMA PRINCIPAL
# ============================================

def main():
    print("="*60)
    print("Backend AWS IoT - Paho MQTT")
    print("="*60)
    
    # Validar configuració
    if not validate_config():
        print("\nRevisa el fitxer .env i els certificats abans de continuar.")
        return
    
    print(f"Endpoint: {AWS_IOT_ENDPOINT}")
    print(f"Port: {AWS_IOT_PORT}")
    print(f"Client ID: {CLIENT_ID}")
    print(f"Subscripció: {SUBSCRIBE_TOPIC}")
    print(f"Publicació cada {PUBLISH_INTERVAL} segons al topic: {PUBLISH_TOPIC}")
    print("="*60 + "\n")

    # Crear client MQTT
    client = mqtt.Client(client_id=CLIENT_ID)
    
    # Assignar callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_publish = on_publish
    
    # Configurar TLS/SSL amb certificats
    client.tls_set(
        ca_certs=PATH_TO_AMAZON_ROOT_CA,
        certfile=PATH_TO_CERTIFICATE,
        keyfile=PATH_TO_PRIVATE_KEY,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLSv1_2,
        ciphers=None
    )
    
    # Habilitar reconnexió automàtica
    client.enable_logger()
    client.reconnect_delay_set(min_delay=1, max_delay=120)
    
    try:
        # Connectar a AWS IoT
        print(f"[{datetime.now()}] Connectant a AWS IoT...")
        client.connect(AWS_IOT_ENDPOINT, AWS_IOT_PORT, keepalive=60)
        
        # Iniciar thread de publicació periòdica
        publish_thread = threading.Thread(target=publish_periodic, args=(client,), daemon=True)
        publish_thread.start()
        
        # Iniciar bucle de connexió (bloquejant)
        print(f"[{datetime.now()}] Iniciant bucle MQTT...\n")
        client.loop_forever()
        
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Interromput per l'usuari. Desconnectant...")
        client.disconnect()
        client.loop_stop()
        print(f"[{datetime.now()}] Desconnectat correctament.")
    
    except Exception as e:
        print(f"[{datetime.now()}] Error: {e}")

if __name__ == "__main__":
    main()