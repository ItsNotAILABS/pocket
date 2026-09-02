export class PocketSuiteClient {
  constructor(options = {}) {
    this.baseUrl = (options.baseUrl || 'https://beta.pocketnova.app').replace(/\/$/, '');
    this.betaHost = options.betaHost || 'beta.pocketnova.app';
    this.token = options.token || null;
  }

  headers(extra = {}) {
    const headers = { 'content-type': 'application/json', ...extra };
    if (this.token) headers.authorization = `Bearer ${this.token}`;
    return headers;
  }

  async request(path, body) {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify(body || {})
    });
    const text = await res.text();
    let payload;
    try { payload = text ? JSON.parse(text) : {}; } catch (_) { payload = { raw: text }; }
    if (!res.ok) throw Object.assign(new Error(`POCKET request failed: ${res.status}`), { status: res.status, payload });
    return payload;
  }

  async submitAgentTask(task) {
    return this.request('/v1/agents/tasks', requireFields(task, ['task_id', 'title', 'operator_approval']));
  }

  async createProductionClaim(claim) {
    return this.request('/v1/production/claims', requireFields(claim, ['claim_id', 'deploy_target', 'verification_evidence', 'operator_approval']));
  }

  async requestDataExport(exportRequest) {
    return this.request('/v1/data/exports', requireFields(exportRequest, ['export_id', 'format', 'operator_approval']));
  }

  async requestPaymentExecution(payment) {
    forbidSensitive(payment);
    return this.request('/v1/payments/executions', requireFields(payment, ['payment_id', 'provider_ref', 'amount', 'currency', 'operator_approval']));
  }

  async requestWalletExecution(walletAction) {
    forbidSensitive(walletAction);
    return this.request('/v1/wallet/executions', requireFields(walletAction, ['wallet_action_id', 'provider_ref', 'chain', 'operator_approval']));
  }

  async localReceipt(event) {
    const payload = { ...event, beta_host: this.betaHost, created_at: new Date().toISOString() };
    const encoded = new TextEncoder().encode(stableStringify(payload));
    const digest = await crypto.subtle.digest('SHA-256', encoded);
    const hash = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
    return { schema: 'pocket.client_receipt.v1', ...payload, hash: `sha256:${hash}` };
  }
}

function requireFields(value, fields) {
  const missing = fields.filter(field => value?.[field] === undefined || value?.[field] === null || value?.[field] === '');
  if (missing.length) throw new Error(`Missing required fields: ${missing.join(', ')}`);
  return value;
}

function forbidSensitive(value) {
  const text = stableStringify(value).toLowerCase();
  const blocked = ['private_key', 'seed phrase', 'mnemonic', 'cvv', 'cvc', 'raw_card', 'pan'];
  const hit = blocked.find(term => text.includes(term));
  if (hit) throw new Error(`Blocked sensitive field detected: ${hit}`);
}

function stableStringify(value) {
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}
