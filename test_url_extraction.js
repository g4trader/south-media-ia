// Teste da função extractSheetId com a URL fornecida pelo usuário

function extractSheetId(url) {
  if (!url) return '';
  
  // Se já é um ID (sem caracteres especiais), retorna como está
  if (!url.includes('/') && !url.includes('?')) {
    return url;
  }
  
  // Extrair ID de URLs do Google Sheets
  const match = url.match(/\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/);
  return match ? match[1] : url;
}

// Testar com a URL fornecida pelo usuário
const userUrl = "https://docs.google.com/spreadsheets/d/1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8/edit?gid=668487440#gid=668487440";

console.log("🧪 Testando extração de ID da planilha:");
console.log("URL fornecida:", userUrl);
console.log("ID extraído:", extractSheetId(userUrl));
console.log("ID esperado:", "1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8");
console.log("✅ Teste passou:", extractSheetId(userUrl) === "1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8");
