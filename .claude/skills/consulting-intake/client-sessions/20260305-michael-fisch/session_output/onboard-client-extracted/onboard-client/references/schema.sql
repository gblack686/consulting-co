-- Fisch Group Standard Client Schema
-- Applied per-project via Supabase MCP apply_migration

-- Clients table: core company identity
CREATE TABLE IF NOT EXISTS clients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_name TEXT NOT NULL,
  legal_name TEXT,
  ein TEXT,                        -- Employer Identification Number
  state_of_incorporation TEXT,
  fiscal_year_end TEXT,            -- e.g. 'December 31'
  primary_address TEXT,
  contact_email TEXT NOT NULL,
  contact_name TEXT,
  billing_email TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Transactions table: financial transaction records imported from QuickBooks/Cin7/bank feeds
CREATE TABLE IF NOT EXISTS transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
  source TEXT NOT NULL,            -- 'quickbooks', 'cin7', 'bank_feed', 'manual'
  source_transaction_id TEXT,      -- ID in the originating system
  transaction_date DATE NOT NULL,
  amount NUMERIC(18,2) NOT NULL,   -- positive = income, negative = expense
  currency TEXT DEFAULT 'USD',
  category TEXT,
  description TEXT,
  account_name TEXT,
  vendor_customer TEXT,
  reconciled BOOLEAN DEFAULT false,
  imported_at TIMESTAMPTZ DEFAULT now()
);

-- Reports table: generated financial reports and snapshots
CREATE TABLE IF NOT EXISTS reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
  report_type TEXT NOT NULL,       -- 'profit_loss', 'balance_sheet', 'cash_flow', 'custom'
  period_start DATE,
  period_end DATE,
  title TEXT,
  data JSONB,                      -- structured report data
  raw_output TEXT,                 -- markdown or HTML rendering
  generated_by TEXT,               -- 'system' or user email
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Users table: client-side team members with portal access
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT,
  role TEXT,                       -- e.g. 'CFO', 'Controller', 'CEO'
  permission_level TEXT DEFAULT 'view_only',  -- 'view_only' or 'full_access'
  is_primary_contact BOOLEAN DEFAULT false,
  is_executive_sponsor BOOLEAN DEFAULT false,
  invited_at TIMESTAMPTZ,
  last_login TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Platform credentials: API keys and connection info for integrated platforms
-- NOTE: In production, key_value should be stored encrypted (e.g., via Supabase Vault)
CREATE TABLE IF NOT EXISTS platform_credentials (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
  platform TEXT NOT NULL,          -- 'quickbooks', 'cin7', 'bank_chase', etc.
  credential_type TEXT NOT NULL,   -- 'api_key', 'oauth_token', 'username_password'
  key_name TEXT NOT NULL,          -- e.g. 'client_id', 'client_secret', 'access_token'
  key_value TEXT,                  -- ⚠️ encrypt before storing sensitive values
  expires_at TIMESTAMPTZ,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Documents table: references to financial documents uploaded or linked
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
  doc_type TEXT NOT NULL,          -- 'prior_financials', 'chart_of_accounts', 'contract', 'custom'
  title TEXT NOT NULL,
  storage_url TEXT,                -- Supabase Storage URL or external link
  fiscal_year INTEGER,
  uploaded_by TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_transactions_client_date
  ON transactions(client_id, transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_reports_client_type
  ON reports(client_id, report_type, period_end DESC);
CREATE INDEX IF NOT EXISTS idx_users_client_email
  ON users(client_id, email);
CREATE INDEX IF NOT EXISTS idx_platform_credentials_client_platform
  ON platform_credentials(client_id, platform);
