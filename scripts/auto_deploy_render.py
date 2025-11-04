#!/usr/bin/env python3
"""
Script automatizado para fazer deploy do Agente Pangeia no Render via API
"""
import os
import sys
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
env_file = Path(__file__).parent.parent / '.env'
load_dotenv(env_file)

# Configurações do Render
RENDER_API_KEY = os.getenv('RENDER_API_KEY', '8ELA-NFLQ-5K8Z-QAV0')
RENDER_API_URL = "https://api.render.com/v1"
HEADERS = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Content-Type": "application/json"
}

# Configurações do serviço
SERVICE_NAME = "pangeia-agent"
REPO_URL = "https://github.com/estevaoantuness/agentefinal"

def list_services():
    """Lista todos os serviços do Render"""
    print("🔍 Verificando serviços existentes...")
    try:
        response = requests.get(f"{RENDER_API_URL}/services", headers=HEADERS, timeout=10)

        if response.status_code == 200:
            data = response.json()
            # A API do Render retorna os serviços em data[0]
            services = data if isinstance(data, list) else data.get('services', [])
            print(f"✅ Encontrados {len(services)} serviço(s)")
            for service in services:
                service_name = service.get('service', {}).get('name') if 'service' in service else service.get('name')
                service_id = service.get('service', {}).get('id') if 'service' in service else service.get('id')
                service_type = service.get('service', {}).get('type') if 'service' in service else service.get('type')
                print(f"   - {service_name} ({service_id}) - {service_type}")
            return services
        elif response.status_code == 401:
            print(f"❌ Erro de autenticação (401). Chave API inválida.")
            print(f"   Configure a chave API correta em RENDER_API_KEY")
            return None
        else:
            print(f"❌ Erro ao listar serviços: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro ao conectar com Render API: {e}")
        return None

def get_service_by_name(name, services):
    """Busca um serviço pelo nome"""
    if not services:
        return None

    for service in services:
        service_data = service.get('service', service)
        if service_data.get('name') == name:
            return service_data
    return None

def trigger_deploy(service_id):
    """Dispara um novo deploy"""
    print(f"\n🚀 Disparando deploy para serviço {service_id}...")

    try:
        response = requests.post(
            f"{RENDER_API_URL}/services/{service_id}/deploys",
            headers=HEADERS,
            timeout=10
        )

        if response.status_code in [200, 201]:
            deploy = response.json()
            print(f"✅ Deploy disparado!")
            print(f"   Deploy ID: {deploy.get('id')}")
            print(f"   Status: {deploy.get('status')}")
            return deploy
        else:
            print(f"❌ Erro ao disparar deploy: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro ao disparar deploy: {e}")
        return None

def main():
    print("═" * 60)
    print("🤖 DEPLOY AUTOMÁTICO - AGENTE PANGEIA NO RENDER")
    print("═" * 60)

    # Verificar serviços existentes
    services = list_services()

    if services is None:
        print("\n⚠️  Não foi possível acessar a API do Render.")
        print("   Opções:")
        print("   1. Configure manualmente via Dashboard: https://dashboard.render.com")
        print("   2. Configure a chave API correta em .env (RENDER_API_KEY)")
        print("\n📋 Configurações necessárias:")
        print(f"   Nome: {SERVICE_NAME}")
        print(f"   Repositório: {REPO_URL}")
        print(f"   Branch: main")
        print(f"   Build Command: ./build.sh")
        print(f"   Start Command: uvicorn src.main:app --host 0.0.0.0 --port $PORT")
        print(f"   Env Vars: Ver CREDENCIAIS_RENDER.txt")
        return

    # Verificar se já existe o serviço
    existing_service = get_service_by_name(SERVICE_NAME, services)

    if existing_service:
        print(f"\n✅ Serviço '{SERVICE_NAME}' já existe!")
        print(f"   ID: {existing_service.get('id')}")

        # Pegar detalhes do serviço
        service_details = existing_service.get('serviceDetails', {})
        url = service_details.get('url') or f"https://{SERVICE_NAME}.onrender.com"
        print(f"   URL: {url}")

        # Disparar redeploy automaticamente
        print(f"\n🔄 Iniciando redeploy automático...")
        deploy = trigger_deploy(existing_service.get('id'))

        if deploy:
            print(f"\n✅ Deploy em andamento!")
            print(f"📊 Acompanhe em: https://dashboard.render.com")
            print(f"🌐 URL do serviço: {url}")
    else:
        print(f"\n❌ Serviço '{SERVICE_NAME}' não encontrado.")
        print(f"\n📋 Para criar o serviço, acesse:")
        print(f"   https://dashboard.render.com/create?type=web")
        print(f"\n⚙️  Configurações:")
        print(f"   Nome: {SERVICE_NAME}")
        print(f"   Repositório: {REPO_URL}")
        print(f"   Branch: main")
        print(f"   Runtime: Python 3")
        print(f"   Build Command: ./build.sh")
        print(f"   Start Command: uvicorn src.main:app --host 0.0.0.0 --port $PORT")
        print(f"   Health Check: /health")
        print(f"\n📝 Env Vars: Veja CREDENCIAIS_RENDER.txt")

    print("\n" + "═" * 60)
    print("✅ Script finalizado!")
    print("═" * 60)

if __name__ == "__main__":
    main()
