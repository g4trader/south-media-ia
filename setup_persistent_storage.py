#!/usr/bin/env python3
"""
Script para configurar o armazenamento persistente no Google Cloud Storage
"""

import os
from google.cloud import storage
from google.cloud.exceptions import Conflict

def create_bucket():
    """Cria o bucket para armazenamento do banco de dados"""
    
    bucket_name = "south-media-ia-database"
    
    print(f"🪣 Criando bucket: {bucket_name}")
    
    try:
        # Inicializar cliente
        client = storage.Client()
        
        # Verificar se bucket já existe
        bucket = client.bucket(bucket_name)
        if bucket.exists():
            print(f"✅ Bucket {bucket_name} já existe")
            return True
        
        # Criar bucket
        bucket = client.create_bucket(bucket_name, location="us-central1")
        print(f"✅ Bucket {bucket_name} criado com sucesso!")
        
        # Configurar permissões (opcional)
        bucket.make_public()
        print(f"✅ Bucket configurado como público")
        
        return True
        
    except Conflict:
        print(f"✅ Bucket {bucket_name} já existe")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar bucket: {e}")
        return False

def test_bucket_access():
    """Testa o acesso ao bucket"""
    
    bucket_name = "south-media-ia-database"
    
    print(f"🧪 Testando acesso ao bucket: {bucket_name}")
    
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        
        if bucket.exists():
            print(f"✅ Bucket acessível")
            
            # Listar objetos
            blobs = list(bucket.list_blobs())
            print(f"📁 Objetos no bucket: {len(blobs)}")
            
            for blob in blobs:
                print(f"  - {blob.name} ({blob.size} bytes)")
            
            return True
        else:
            print(f"❌ Bucket não existe")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao acessar bucket: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Configurando armazenamento persistente...")
    
    # Criar bucket
    if create_bucket():
        # Testar acesso
        test_bucket_access()
    
    print("🎯 Configuração concluída!")
