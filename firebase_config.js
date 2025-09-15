// Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyBXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    authDomain: "south-media-ia.firebaseapp.com",
    projectId: "south-media-ia",
    storageBucket: "south-media-ia.appspot.com",
    messagingSenderId: "123456789012",
    appId: "1:123456789012:web:abcdefghijklmnopqrstuv"
};

// Initialize Firebase
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, doc, getDoc, setDoc, updateDoc, deleteDoc, query, where, getDocs, addDoc, orderBy, limit } from 'firebase/firestore';

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// Database Collections
const COLLECTIONS = {
    USERS: 'users',
    COMPANIES: 'companies',
    DASHBOARDS: 'dashboards',
    ROLES: 'roles',
    PERMISSIONS: 'permissions',
    SESSIONS: 'sessions',
    LOGS: 'logs'
};

// Database Service Class
class DatabaseService {
    constructor() {
        this.db = db;
        this.collections = COLLECTIONS;
    }

    // Generic CRUD operations
    async create(collectionName, data, docId = null) {
        try {
            const collectionRef = collection(this.db, collectionName);
            if (docId) {
                await setDoc(doc(collectionRef, docId), {
                    ...data,
                    created_at: new Date(),
                    updated_at: new Date()
                });
                return docId;
            } else {
                const docRef = await addDoc(collectionRef, {
                    ...data,
                    created_at: new Date(),
                    updated_at: new Date()
                });
                return docRef.id;
            }
        } catch (error) {
            console.error(`Erro ao criar documento em ${collectionName}:`, error);
            throw error;
        }
    }

    async read(collectionName, docId) {
        try {
            const docRef = doc(this.db, collectionName, docId);
            const docSnap = await getDoc(docRef);
            
            if (docSnap.exists()) {
                return { id: docSnap.id, ...docSnap.data() };
            } else {
                return null;
            }
        } catch (error) {
            console.error(`Erro ao ler documento de ${collectionName}:`, error);
            throw error;
        }
    }

    async update(collectionName, docId, data) {
        try {
            const docRef = doc(this.db, collectionName, docId);
            await updateDoc(docRef, {
                ...data,
                updated_at: new Date()
            });
            return true;
        } catch (error) {
            console.error(`Erro ao atualizar documento em ${collectionName}:`, error);
            throw error;
        }
    }

    async delete(collectionName, docId) {
        try {
            const docRef = doc(this.db, collectionName, docId);
            await deleteDoc(docRef);
            return true;
        } catch (error) {
            console.error(`Erro ao deletar documento de ${collectionName}:`, error);
            throw error;
        }
    }

    async query(collectionName, conditions = [], orderByField = null, limitCount = null) {
        try {
            let q = collection(this.db, collectionName);
            
            // Add where conditions
            conditions.forEach(condition => {
                q = query(q, where(condition.field, condition.operator, condition.value));
            });
            
            // Add ordering
            if (orderByField) {
                q = query(q, orderBy(orderByField));
            }
            
            // Add limit
            if (limitCount) {
                q = query(q, limit(limitCount));
            }
            
            const querySnapshot = await getDocs(q);
            const results = [];
            querySnapshot.forEach((doc) => {
                results.push({ id: doc.id, ...doc.data() });
            });
            
            return results;
        } catch (error) {
            console.error(`Erro ao consultar ${collectionName}:`, error);
            throw error;
        }
    }

    // User-specific operations
    async createUser(userData) {
        return await this.create(this.collections.USERS, userData);
    }

    async getUser(userId) {
        return await this.read(this.collections.USERS, userId);
    }

    async getUserByUsername(username) {
        const users = await this.query(this.collections.USERS, [
            { field: 'username', operator: '==', value: username }
        ]);
        return users.length > 0 ? users[0] : null;
    }

    async updateUser(userId, userData) {
        return await this.update(this.collections.USERS, userId, userData);
    }

    async deleteUser(userId) {
        return await this.delete(this.collections.USERS, userId);
    }

    // Company-specific operations
    async createCompany(companyData) {
        return await this.create(this.collections.COMPANIES, companyData);
    }

    async getCompany(companyId) {
        return await this.read(this.collections.COMPANIES, companyId);
    }

    async getAllCompanies() {
        return await this.query(this.collections.COMPANIES, [], 'name');
    }

    async updateCompany(companyId, companyData) {
        return await this.update(this.collections.COMPANIES, companyId, companyData);
    }

    async deleteCompany(companyId) {
        return await this.delete(this.collections.COMPANIES, companyId);
    }

    // Dashboard-specific operations
    async createDashboard(dashboardData) {
        return await this.create(this.collections.DASHBOARDS, dashboardData);
    }

    async getDashboard(dashboardId) {
        return await this.read(this.collections.DASHBOARDS, dashboardId);
    }

    async getDashboardsByCompany(companyId) {
        return await this.query(this.collections.DASHBOARDS, [
            { field: 'company_id', operator: '==', value: companyId }
        ], 'name');
    }

    async getAllDashboards() {
        return await this.query(this.collections.DASHBOARDS, [], 'name');
    }

    async updateDashboard(dashboardId, dashboardData) {
        return await this.update(this.collections.DASHBOARDS, dashboardId, dashboardData);
    }

    async deleteDashboard(dashboardId) {
        return await this.delete(this.collections.DASHBOARDS, dashboardId);
    }

    // Session management
    async createSession(sessionData) {
        return await this.create(this.collections.SESSIONS, sessionData);
    }

    async getSession(sessionId) {
        return await this.read(this.collections.SESSIONS, sessionId);
    }

    async updateSession(sessionId, sessionData) {
        return await this.update(this.collections.SESSIONS, sessionId, sessionData);
    }

    async deleteSession(sessionId) {
        return await this.delete(this.collections.SESSIONS, sessionId);
    }

    // Logging
    async logActivity(activity, userId, details = {}) {
        return await this.create(this.collections.LOGS, {
            activity,
            user_id: userId,
            details,
            timestamp: new Date()
        });
    }

    // Migration from localStorage to Firestore
    async migrateFromLocalStorage() {
        try {
            console.log('🔄 Iniciando migração do localStorage para Firestore...');
            
            // Check if migration already done
            const migrationCheck = await this.query(this.collections.LOGS, [
                { field: 'activity', operator: '==', value: 'migration_completed' }
            ]);
            
            if (migrationCheck.length > 0) {
                console.log('✅ Migração já foi realizada anteriormente');
                return true;
            }

            // Get localStorage data
            const localData = localStorage.getItem('dashboard_auth_system');
            if (!localData) {
                console.log('ℹ️ Nenhum dado encontrado no localStorage para migrar');
                return true;
            }

            const systemData = JSON.parse(localData);
            
            // Migrate companies
            if (systemData.companies) {
                for (const company of systemData.companies) {
                    await this.createCompany(company);
                }
                console.log(`✅ ${systemData.companies.length} empresas migradas`);
            }

            // Migrate users
            if (systemData.users) {
                for (const user of systemData.users) {
                    await this.createUser(user);
                }
                console.log(`✅ ${systemData.users.length} usuários migrados`);
            }

            // Migrate dashboards
            if (systemData.dashboards) {
                for (const dashboard of systemData.dashboards) {
                    await this.createDashboard(dashboard);
                }
                console.log(`✅ ${systemData.dashboards.length} dashboards migrados`);
            }

            // Log migration completion
            await this.logActivity('migration_completed', 'system', {
                companies: systemData.companies?.length || 0,
                users: systemData.users?.length || 0,
                dashboards: systemData.dashboards?.length || 0
            });

            console.log('🎉 Migração concluída com sucesso!');
            return true;

        } catch (error) {
            console.error('❌ Erro durante migração:', error);
            throw error;
        }
    }
}

// Export database service
export const databaseService = new DatabaseService();
export { COLLECTIONS };
