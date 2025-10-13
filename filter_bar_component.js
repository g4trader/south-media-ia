// Componente de Barra de Filtro - JavaScript
class FilterBar {
  constructor() {
    this.startDate = null;
    this.endDate = null;
    this.activeFilter = 'todos';
    this.callbacks = {
      onDateChange: null,
      onQuickFilter: null
    };
    
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.setDefaultDates();
    this.updatePeriodDisplay();
  }

  setupEventListeners() {
    // Event listeners para inputs de data
    const startDateInput = document.getElementById('filter-start-date');
    const endDateInput = document.getElementById('filter-end-date');
    
    if (startDateInput) {
      startDateInput.addEventListener('change', (e) => {
        this.startDate = e.target.value;
        this.updatePeriodDisplay();
        this.triggerDateChange();
      });
    }
    
    if (endDateInput) {
      endDateInput.addEventListener('change', (e) => {
        this.endDate = e.target.value;
        this.updatePeriodDisplay();
        this.triggerDateChange();
      });
    }

    // Event listeners para botões de filtro rápido
    document.querySelectorAll('.quick-filter-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.handleQuickFilter(e.target.dataset.filter);
      });
    });
  }

  setDefaultDates() {
    const today = new Date();
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
    this.startDate = this.formatDateForInput(thirtyDaysAgo);
    this.endDate = this.formatDateForInput(today);
    
    // Atualizar inputs se existirem
    const startDateInput = document.getElementById('filter-start-date');
    const endDateInput = document.getElementById('filter-end-date');
    
    if (startDateInput) startDateInput.value = this.startDate;
    if (endDateInput) endDateInput.value = this.endDate;
  }

  handleQuickFilter(filterType) {
    const today = new Date();
    let startDate;
    
    // Remover active de todos os botões
    document.querySelectorAll('.quick-filter-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    
    // Adicionar active ao botão clicado
    const activeBtn = document.querySelector(`[data-filter="${filterType}"]`);
    if (activeBtn) activeBtn.classList.add('active');
    
    switch (filterType) {
      case 'hoje':
        startDate = today;
        break;
      case '7-dias':
        startDate = new Date(today);
        startDate.setDate(today.getDate() - 7);
        break;
      case '30-dias':
        startDate = new Date(today);
        startDate.setDate(today.getDate() - 30);
        break;
      case 'todos':
        startDate = null;
        break;
    }
    
    this.activeFilter = filterType;
    
    if (startDate) {
      this.startDate = this.formatDateForInput(startDate);
      this.endDate = this.formatDateForInput(today);
      
      // Atualizar inputs
      const startDateInput = document.getElementById('filter-start-date');
      const endDateInput = document.getElementById('filter-end-date');
      
      if (startDateInput) startDateInput.value = this.startDate;
      if (endDateInput) endDateInput.value = this.endDate;
    } else {
      // Para "todos", limpar datas
      this.startDate = null;
      this.endDate = null;
      
      const startDateInput = document.getElementById('filter-start-date');
      const endDateInput = document.getElementById('filter-end-date');
      
      if (startDateInput) startDateInput.value = '';
      if (endDateInput) endDateInput.value = '';
    }
    
    this.updatePeriodDisplay();
    this.triggerDateChange();
  }

  updatePeriodDisplay() {
    const displayElement = document.getElementById('period-display');
    if (!displayElement) return;
    
    if (this.startDate && this.endDate) {
      const startFormatted = this.formatDateForDisplay(this.startDate);
      const endFormatted = this.formatDateForDisplay(this.endDate);
      displayElement.textContent = `Período: ${startFormatted} até ${endFormatted}`;
    } else {
      displayElement.textContent = 'Período: Todos os dados';
    }
  }

  formatDateForInput(date) {
    if (typeof date === 'string') return date;
    return date.toISOString().split('T')[0];
  }

  formatDateForDisplay(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  }

  triggerDateChange() {
    if (this.callbacks.onDateChange) {
      this.callbacks.onDateChange({
        startDate: this.startDate,
        endDate: this.endDate,
        activeFilter: this.activeFilter
      });
    }
  }

  // Método para definir callback de mudança de data
  onDateChange(callback) {
    this.callbacks.onDateChange = callback;
  }

  // Método para obter filtros atuais
  getCurrentFilters() {
    return {
      startDate: this.startDate,
      endDate: this.endDate,
      activeFilter: this.activeFilter
    };
  }

  // Método para aplicar filtros aos dados
  applyDateFilter(data, dateField = 'date') {
    if (!this.startDate && !this.endDate) {
      return data;
    }

    return data.filter(item => {
      const itemDate = new Date(item[dateField]);
      const startDate = this.startDate ? new Date(this.startDate) : null;
      const endDate = this.endDate ? new Date(this.endDate) : null;

      if (startDate && itemDate < startDate) return false;
      if (endDate && itemDate > endDate) return false;

      return true;
    });
  }

  // Método para filtrar dados diários
  filterDailyData(dailyData) {
    return this.applyDateFilter(dailyData, 'date');
  }

  // Método para recarregar dashboard com filtros aplicados
  reloadDashboard() {
    // Esta função será chamada quando os filtros mudarem
    // Pode ser sobrescrita para integrar com o sistema de dados específico
    console.log('Filtros aplicados:', this.getCurrentFilters());
  }
}

// Inicializar automaticamente quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
  window.filterBar = new FilterBar();
  
  // Configurar callback para recarregar dados quando filtros mudarem
  window.filterBar.onDateChange((filters) => {
    console.log('Filtros alterados:', filters);
    
    // Aqui você pode integrar com o sistema de dados do dashboard
    // Por exemplo, recarregar dados da API ou filtrar dados locais
    if (typeof window.reloadDashboardData === 'function') {
      window.reloadDashboardData(filters);
    }
  });
});
