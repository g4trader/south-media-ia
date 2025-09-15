// Template de Configuração Firebase
// Substitua os valores abaixo pelas suas credenciais do Firebase

const firebaseConfig = {
    // Substitua pela sua API Key
    apiKey: "SUA_API_KEY_AQUI",
    
    // Substitua pelo seu Auth Domain
    authDomain: "seu-projeto.firebaseapp.com",
    
    // Substitua pelo seu Project ID
    projectId: "seu-projeto-id",
    
    // Substitua pelo seu Storage Bucket
    storageBucket: "seu-projeto.appspot.com",
    
    // Substitua pelo seu Messaging Sender ID
    messagingSenderId: "123456789012",
    
    // Substitua pelo seu App ID
    appId: "1:123456789012:web:abcdefghijklmnopqrstuv"
};

// Instruções:
// 1. Acesse https://console.firebase.google.com/
// 2. Crie um novo projeto ou selecione um existente
// 3. Vá para "Configurações do projeto" (ícone de engrenagem)
// 4. Role para baixo até "Seus aplicativos"
// 5. Clique em "Adicionar app" e escolha "Web" (ícone </>)
// 6. Copie a configuração que aparece
// 7. Substitua os valores acima
// 8. Renomeie este arquivo para firebase_config.js
// 9. O sistema híbrido detectará automaticamente o Firebase

export { firebaseConfig };
