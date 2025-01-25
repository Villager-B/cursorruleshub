class CursorRulesHub {
    constructor() {
        this.repositories = [];
        this.filteredRepositories = [];
        this.currentPage = 1;
        this.itemsPerPage = 12;
        this.languageFilter = '';
        this.sortOption = 'stars';
        this.searchQuery = '';
        this.languageIcons = {
            'JavaScript': 'javascript',
            'TypeScript': 'typescript',
            'Python': 'python',
            'Java': 'java',
            'C++': 'cplusplus',
            'C#': 'csharp',
            'Ruby': 'ruby',
            'Go': 'go',
            'Rust': 'rust',
            'PHP': 'php',
            'Swift': 'swift',
            'Kotlin': 'kotlin',
            'Dart': 'dart',
            'HTML': 'html5',
            'CSS': 'css3',
            'Shell': 'shell',
            'Vue': 'vue-dot-js',
            'React': 'react',
            'Angular': 'angular',
        };

        this.initializeElements();
        this.attachEventListeners();
        this.loadData();
    }

    initializeElements() {
        this.searchInput = document.getElementById('searchInput');
        this.languageSelect = document.getElementById('languageFilter');
        this.sortSelect = document.getElementById('sortOption');
        this.repositoriesList = document.getElementById('repositoriesList');
        this.paginationContainer = document.getElementById('pagination');
        this.lastUpdateElement = document.getElementById('lastUpdate');
    }

    attachEventListeners() {
        this.searchInput.addEventListener('input', () => {
            this.searchQuery = this.searchInput.value.toLowerCase();
            this.currentPage = 1;
            this.filterAndRenderRepositories();
        });

        this.languageSelect.addEventListener('change', () => {
            this.languageFilter = this.languageSelect.value;
            this.currentPage = 1;
            this.filterAndRenderRepositories();
        });

        this.sortSelect.addEventListener('change', () => {
            this.sortOption = this.sortSelect.value;
            this.currentPage = 1;
            this.filterAndRenderRepositories();
        });
    }

    async loadData() {
        try {
            const response = await fetch('./data/cursorrules_data.json');
            const data = await response.json();
            this.repositories = data.repositories;
            
            // 最終更新日時を表示
            const lastUpdated = new Date(data.last_updated);
            this.lastUpdateElement.textContent = `Last Update: ${lastUpdated.toUTCString()}`;
            
            // 言語フィルターのオプションを設定
            const languages = [...new Set(this.repositories.map(repo => repo.language).filter(Boolean))];
            languages.sort();
            languages.forEach(language => {
                const option = document.createElement('option');
                option.value = language;
                option.textContent = language;
                this.languageSelect.appendChild(option);
            });

            this.filterAndRenderRepositories();
        } catch (error) {
            console.error('Failed to load data:', error);
            this.showError('Failed to load data. Please try again later.');
        }
    }

    filterAndRenderRepositories() {
        // フィルタリング
        this.filteredRepositories = this.repositories.filter(repo => {
            const matchesLanguage = !this.languageFilter || repo.language === this.languageFilter;
            const matchesSearch = !this.searchQuery || 
                repo.name.toLowerCase().includes(this.searchQuery) ||
                (repo.description && repo.description.toLowerCase().includes(this.searchQuery));
            return matchesLanguage && matchesSearch;
        });

        // ソート
        this.filteredRepositories.sort((a, b) => {
            if (this.sortOption === 'stars') {
                return b.stars - a.stars;
            } else {
                return new Date(b.updated_at) - new Date(a.updated_at);
            }
        });

        this.renderRepositories();
        this.renderPagination();
    }

    getLanguageIcon(language) {
        if (!language) return '';
        // 言語名を小文字に変換し、特殊文字を処理
        const normalizedLanguage = language.toLowerCase()
            .replace(/\+/g, 'plus')
            .replace(/#/g, 'sharp')
            .replace(/\./g, 'dot');
        
        // アイコンのクラス名を生成
        const iconClass = `si-${normalizedLanguage}`;
        
        return `<i class="${iconClass}"></i>`;
    }

    renderRepositories() {
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageRepositories = this.filteredRepositories.slice(startIndex, endIndex);

        this.repositoriesList.innerHTML = pageRepositories.map(repo => `
            <div class="repository-card neu-card">
                <h3>
                    <a href="${repo.url}" target="_blank" rel="noopener noreferrer">
                        ${repo.name}
                    </a>
                </h3>
                <p>${repo.description || 'No description available.'}</p>
                <div class="repository-meta">
                    <span class="repository-language">${repo.language || 'Unknown'}</span>
                    <span class="repository-stars">⭐ ${repo.stars}</span>
                </div>
                <a href="${repo.cursorrules_url}" target="_blank" rel="noopener noreferrer" class="neu-button">
                    View .cursorrules
                </a>
            </div>
        `).join('');
    }

    renderPagination() {
        const totalPages = Math.ceil(this.filteredRepositories.length / this.itemsPerPage);
        
        if (totalPages <= 1) {
            this.paginationContainer.innerHTML = '';
            return;
        }

        const pages = [];
        for (let i = 1; i <= totalPages; i++) {
            if (
                i === 1 ||
                i === totalPages ||
                (i >= this.currentPage - 1 && i <= this.currentPage + 1)
            ) {
                pages.push(i);
            } else if (pages[pages.length - 1] !== '...') {
                pages.push('...');
            }
        }

        this.paginationContainer.innerHTML = pages.map(page => {
            if (page === '...') {
                return '<span class="pagination-ellipsis">...</span>';
            }
            return `
                <button class="neu-button ${page === this.currentPage ? 'active' : ''}"
                        onclick="app.goToPage(${page})"
                        ${page === this.currentPage ? 'disabled' : ''}>
                    ${page}
                </button>
            `;
        }).join('');
    }

    goToPage(page) {
        this.currentPage = page;
        this.filterAndRenderRepositories();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    showError(message) {
        this.repositoriesList.innerHTML = `
            <div class="error-message">
                <p>${message}</p>
            </div>
        `;
    }
}

// アプリケーションの初期化
const app = new CursorRulesHub();
