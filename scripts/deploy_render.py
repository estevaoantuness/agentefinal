#!/usr/bin/env python3
"""
Script para fazer deploy do Agente Pangeia no Render via API
"""
import os
import sys
import json
import requests
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
    response = requests.get(f"{RENDER_API_URL}/services", headers=HEADERS)

    if response.status_code == 200:
        services = response.json()
        print(f"✅ Encontrados {len(services)} serviço(s)")
        for service in services:
            print(f"   - {service['name']} ({service['id']}) - {service['type']}")
        return services
    else:
        print(f"❌ Erro ao listar serviços: {response.status_code}")
        print(f"   Resposta: {response.text}")
        return []

def get_service_by_name(name):
    """Busca um serviço pelo nome"""
    services = list_services()
    for service in services:
        if service.get('name') == name:
            return service
    return None

def create_service():
    """Cria um novo serviço no Render"""
    print(f"\n🚀 Criando novo serviço '{SERVICE_NAME}'...")

    # Carregar env vars do .env
    env_vars = {
        "DATABASE_URL": os.getenv('DATABASE_URL'),
        "EVOLUTION_API_URL": os.getenv('EVOLUTION_API_URL'),
        "EVOLUTION_API_KEY": os.getenv('EVOLUTION_API_KEY'),
        "EVOLUTION_INSTANCE_NAME": os.getenv('EVOLUTION_INSTANCE_NAME'),
        "NOTION_API_KEY": os.getenv('NOTION_API_KEY'),
        "NOTION_DATABASE_ID": os.getenv('NOTION_DATABASE_ID'),
        "OPENAI_API_KEY": os.getenv('OPENAI_API_KEY'),
        "OPENAI_MODEL": os.getenv('OPENAI_MODEL', 'gpt5-nano'),
        "APP_HOST": "0.0.0.0",
        "DEBUG": "False",
        "LOG_LEVEL": "INFO",
        "TIMEZONE": "America/Sao_Paulo",
        "AGENT_TEMPERATURE": "0.7",
        "AGENT_MAX_ITERATIONS": "5",
    }

    # Converter para formato do Render
    env_vars_list = [{"key": k, "value": v} for k, v in env_vars.items() if v]

    payload = {
        "type": "web_service",
        "name": SERVICE_NAME,
        "repo": REPO_URL,
        "branch": "main",
        "runtime": "python",
        "plan": "free",
        "region": "oregon",
        "buildCommand": "./build.sh",
        "startCommand": "uvicorn src.main:app --host 0.0.0.0 --port $PORT",
        "healthCheckPath": "/health",
        "autoDeploy": "yes",
        "envVars": env_vars_list
    }

    response = requests.post(
        f"{RENDER_API_URL}/services",
        headers=HEADERS,
        json=payload
    )

    if response.status_code in [200, 201]:
        service = response.json()
        print(f"✅ Serviço criado com sucesso!")
        print(f"   ID: {service.get('id')}")
        print(f"   Nome: {service.get('name')}")
        print(f"   URL: {service.get('serviceDetails', {}).get('url')}")
        return service
    else:
        print(f"❌ Erro ao criar serviço: {response.status_code}")
        print(f"   Resposta: {response.text}")
        return None

def trigger_deploy(service_id):
    """Dispara um novo deploy"""
    print(f"\n🚀 Disparando deploy para serviço {service_id}...")

    response = requests.post(
        f"{RENDER_API_URL}/services/{service_id}/deploys",
        headers=HEADERS
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

def main():
    print("═" * 60)
    print("🤖 DEPLOY AUTOMÁTICO - AGENTE PANGEIA NO RENDER")
    print("═" * 60)

    # Verificar se já existe o serviço
    existing_service = get_service_by_name(SERVICE_NAME)

    if existing_service:
        print(f"\n✅ Serviço '{SERVICE_NAME}' já existe!")
        print(f"   ID: {existing_service.get('id')}")
        print(f"   URL: {existing_service.get('serviceDetails', {}).get('url')}")

        choice = input("\n🔄 Deseja fazer um novo deploy? (s/n): ")
        if choice.lower() == 's':
            trigger_deploy(existing_service.get('id'))
        else:
            print("⏭️  Deploy cancelado.")
    else:
        print(f"\n❌ Serviço '{SERVICE_NAME}' não encontrado.")
        choice = input("\n🆕 Deseja criar um novo serviço? (s/n): ")

        if choice.lower() == 's':
            service = create_service()
            if service:
                print("\n✅ Serviço criado! O deploy será iniciado automaticamente.")
                print(f"\n📊 Acompanhe em: https://dashboard.render.com")
        else:
            print("⏭️  Criação cancelada.")

    print("\n" + "═" * 60)
    print("✅ Script finalizado!")
    print("═" * 60)

if __name__ == "__main__":
    main()
