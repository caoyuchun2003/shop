/**
 * 百度 CFC 网关 — 邻里小店
 *
 * HTTPS 入口 + CORS，把 /api/* 与 /health 转发到 BCC。
 * 会话用前端 X-Session-Id，不依赖 Cookie。
 *
 * 环境变量:
 *   BACKEND_URL  - 例如 http://180.76.180.105/shop-api 或 http://IP:8020
 *   ALLOW_ORIGIN - 例如 https://shop.yuchuntest.com
 */
'use strict';

const http = require('http');
const https = require('https');
const { URL } = require('url');

const BACKEND_URL = process.env.BACKEND_URL || '';
const ALLOW_ORIGIN = process.env.ALLOW_ORIGIN || '*';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': ALLOW_ORIGIN,
  'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-Session-Id, X-Admin-Token',
  'Access-Control-Allow-Credentials': 'true',
  'Access-Control-Max-Age': '86400',
};

function respond(statusCode, body, extraHeaders) {
  return {
    isBase64Encoded: false,
    statusCode,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      ...CORS_HEADERS,
      ...(extraHeaders || {}),
    },
    body: typeof body === 'string' ? body : JSON.stringify(body),
  };
}

function normalizePath(rawPath) {
  let path = rawPath || '/';
  // CFC 可能带函数前缀，只保留 /api 或 /health 起的部分
  const apiIdx = path.indexOf('/api');
  if (apiIdx >= 0) return path.slice(apiIdx);
  const healthIdx = path.indexOf('/health');
  if (healthIdx >= 0) return path.slice(healthIdx);
  return path;
}

function allowed(path, method) {
  if (path === '/health' || path.startsWith('/health?')) return method === 'GET';
  if (path === '/api' || path.startsWith('/api/')) return true;
  return false;
}

function forward(method, path, query, body, incomingHeaders) {
  return new Promise((resolve, reject) => {
    const base = String(BACKEND_URL || '').replace(/\/$/, '');
    const url = new URL(base + path);
    for (const [k, v] of Object.entries(query || {})) {
      if (v != null) url.searchParams.set(k, String(v));
    }
    const lib = url.protocol === 'https:' ? https : http;
    const headers = {
      'Content-Type': incomingHeaders['content-type'] || 'application/json',
    };
    if (incomingHeaders['x-session-id']) headers['X-Session-Id'] = incomingHeaders['x-session-id'];
    if (incomingHeaders['x-admin-token']) headers['X-Admin-Token'] = incomingHeaders['x-admin-token'];
    if (method !== 'GET' && method !== 'HEAD') {
      headers['Content-Length'] = Buffer.byteLength(body || '');
    }
    const req = lib.request(url, { method, headers, timeout: 30000 }, (res) => {
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () =>
        resolve({ statusCode: res.statusCode, body: Buffer.concat(chunks).toString('utf-8') })
      );
    });
    req.on('timeout', () => req.destroy(new Error('后端响应超时')));
    req.on('error', reject);
    if (method !== 'GET' && method !== 'HEAD' && body) req.write(body);
    req.end();
  });
}

exports.handler = async (event) => {
  const method = (event.httpMethod || '').toUpperCase();
  const path = normalizePath(event.path || '/');
  const headersIn = {};
  for (const [k, v] of Object.entries(event.headers || {})) {
    headersIn[String(k).toLowerCase()] = v;
  }

  if (method === 'OPTIONS') {
    return { isBase64Encoded: false, statusCode: 204, headers: CORS_HEADERS, body: '' };
  }
  if (!BACKEND_URL) {
    return respond(500, { error: '网关未配置 BACKEND_URL' });
  }
  if (!allowed(path, method)) {
    return respond(404, { error: '未知路径' });
  }

  let body = event.body || '';
  if (event.isBase64Encoded) {
    body = Buffer.from(body, 'base64').toString('utf-8');
  }
  if (Buffer.byteLength(body) > 256 * 1024) {
    return respond(413, { error: '请求体过大' });
  }

  try {
    const upstream = await forward(method, path, event.queryStringParameters, body, headersIn);
    return respond(upstream.statusCode || 502, upstream.body);
  } catch (err) {
    return respond(502, { error: `网关转发失败:${err.message}` });
  }
};
