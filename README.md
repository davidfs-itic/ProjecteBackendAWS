# Backend AWS IoT amb Paho MQTT

Backend en Python per connectar-se a AWS IoT Core, subscriure's a topics i publicar missatges periòdicament.

## 📋 Requisits

- Python 3.8 o superior
- Certificats d'AWS IoT (certificat del dispositiu, clau privada i Root CA)
- Endpoint d'AWS IoT Core

## 🚀 Instal·lació

### 1. Clonar el repositori

```bash
git clone <url-del-repositori>
cd <directori-del-projecte>
```

### 2. Crear entorn virtual (recomanat)

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instal·lar dependències

```bash
pip install -r requirements.txt
```

### 4. Configurar variables d'entorn

Copia el fitxer `.env.example` a `.env` i omple les teves dades:

```bash
cp .env.example .env
```

Edita el fitxer `.env` amb els teus valors:

```env
AWS_IOT_ENDPOINT=your-endpoint.iot.region.amazonaws.com
AWS_IOT_PORT=8883

PATH_TO_CERTIFICATE=/path/to/certificate.pem.crt
PATH_TO_PRIVATE_KEY=/path/to/private.pem.key
PATH_TO_AMAZON_ROOT_CA=/path/to/AmazonRootCA1.pem

SUBSCRIBE_TOPIC=escola/#
PUBLISH_TOPIC=escola
PUBLISH_INTERVAL=10
```

### 5. Col·locar els certificats

Crea un directori `certificates/` i col·loca els teus certificats d'AWS IoT:

```bash
mkdir certificates
# Copia els certificats al directori
```

## ▶️ Execució

```bash
python3 main.py
```

El programa:
- Es connectarà a AWS IoT Core
- Se subscriurà al topic configurat (per defecte `escola/#`)
- Publicarà missatges periòdicament al topic configurat (per defecte `escola`)
- Mostrarà per consola tots els missatges rebuts

## 📁 Estructura del projecte

```
.
├── main.py                 # Programa principal
├── requirements.txt        # Dependències Python
├── .env.example           # Exemple de configuració
├── .env                   # Configuració (no es puja al repositori)
├── .gitignore            # Fitxers a ignorar per Git
├── README.md             # Aquest fitxer
└── certificates/         # Directori per certificats (no es puja al repositori)
    ├── certificate.pem.crt
    ├── private.pem.key
    └── AmazonRootCA1.pem
```

## 🐳 Docker

### Construir la imatge

```bash
docker build -t aws-iot-backend .
```

### Executar amb Docker

```bash
docker run -d \
  --name aws-iot-backend \
  --env-file .env \
  -v $(pwd)/certificates:/app/certificates:ro \
  aws-iot-backend
```

### Executar amb Docker Compose (recomanat)

```bash
# Iniciar el servei
docker-compose up -d

# Veure logs
docker-compose logs -f

# Aturar el servei
docker-compose down
```

### Veure logs del contenidor

```bash
# Amb Docker
docker logs -f aws-iot-backend

# Amb Docker Compose
docker-compose logs -f
```

## ⚙️ Configuració

Totes les variables es configuren al fitxer `.env`:

| Variable | Descripció | Per defecte |
|----------|------------|-------------|
| `AWS_IOT_ENDPOINT` | Endpoint d'AWS IoT | - |
| `AWS_IOT_PORT` | Port MQTT amb TLS | 8883 |
| `PATH_TO_CERTIFICATE` | Path al certificat del dispositiu | - |
| `PATH_TO_PRIVATE_KEY` | Path a la clau privada | - |
| `PATH_TO_AMAZON_ROOT_CA` | Path al certificat root d'Amazon | - |
| `SUBSCRIBE_TOPIC` | Topic per subscripció | - |
| `PUBLISH_TOPIC` | Topic per publicació | - |
| `PUBLISH_INTERVAL` | Interval de publicació (segons) | 10 |
| `CLIENT_ID` | ID del client MQTT (opcional) | auto-generat |

## 📝 Notes

- Els certificats **NO** s'han de pujar al repositori (estan al `.gitignore`)
- El programa té reconnexió automàtica en cas de pèrdua de connexió
- Els missatges es publiquen amb QoS 1 per assegurar la entrega

## 🔒 Seguretat

⚠️ **IMPORTANT**: Mai pugis els certificats o el fitxer `.env` al repositori Git. Aquests fitxers contenen informació sensible.

## 📄 Llicència

[La teva llicència aquí]