-- Schema do banco de dados para persistência de campanhas
-- PostgreSQL

-- Criar banco de dados se não existir
CREATE DATABASE IF NOT EXISTS south_media_dashboards;

-- Conectar ao banco
\c south_media_dashboards;

-- Tabela para armazenar configurações de campanhas
CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    campaign_key VARCHAR(255) UNIQUE NOT NULL,
    client VARCHAR(255) NOT NULL,
    campaign_name VARCHAR(255) NOT NULL,
    sheet_id VARCHAR(255) NOT NULL,
    channel VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabela para cache de dados extraídos (opcional, para performance)
CREATE TABLE IF NOT EXISTS campaign_data_cache (
    id SERIAL PRIMARY KEY,
    campaign_key VARCHAR(255) NOT NULL,
    data_json JSONB NOT NULL,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_key) REFERENCES campaigns(campaign_key) ON DELETE CASCADE
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_campaigns_key ON campaigns(campaign_key);
CREATE INDEX IF NOT EXISTS idx_campaigns_client ON campaigns(client);
CREATE INDEX IF NOT EXISTS idx_cache_campaign_key ON campaign_data_cache(campaign_key);
CREATE INDEX IF NOT EXISTS idx_cache_extracted_at ON campaign_data_cache(extracted_at);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_campaigns_updated_at 
    BEFORE UPDATE ON campaigns 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Inserir dados de exemplo (opcional)
-- INSERT INTO campaigns (campaign_key, client, campaign_name, sheet_id, channel) 
-- VALUES ('copacol_institucional_30s', 'Copacol', 'Institucional 30s', '1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8', 'Video Programática')
-- ON CONFLICT (campaign_key) DO NOTHING;

