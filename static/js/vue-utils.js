const VueUtils = {
    createApp(options = {}) {
        const { createApp, ref, computed, watch, onMounted, onUnmounted } = Vue;
        
        const defaultOptions = {
            el: '#app',
            data: {},
            computed: {},
            methods: {},
            watch: {},
            mounted: () => {},
            unmounted: () => {}
        };
        
        const mergedOptions = {
            ...defaultOptions,
            ...options
        };
        
        const setup = () => {
            const state = {};
            const computedProps = {};
            const methods = {};
            
            Object.keys(mergedOptions.data).forEach(key => {
                state[key] = ref(mergedOptions.data[key]);
            });
            
            Object.keys(mergedOptions.computed).forEach(key => {
                computedProps[key] = computed(mergedOptions.computed[key].bind(state));
            });
            
            Object.keys(mergedOptions.methods).forEach(key => {
                methods[key] = mergedOptions.methods[key].bind({ ...state, ...computedProps, ...methods });
            });
            
            onMounted(() => {
                mergedOptions.mounted.call({ ...state, ...computedProps, ...methods });
            });
            
            onUnmounted(() => {
                mergedOptions.unmounted.call({ ...state, ...computedProps, ...methods });
            });
            
            Object.keys(mergedOptions.watch).forEach(key => {
                watch(state[key], mergedOptions.watch[key]);
            });
            
            return {
                ...state,
                ...computedProps,
                ...methods
            };
        };
        
        const app = createApp({ setup });
        return app.mount(mergedOptions.el);
    },
    
    initFromDjango(elId = 'app') {
        const dataElement = document.getElementById('vue-data');
        const data = dataElement ? JSON.parse(dataElement.textContent) : {};
        
        return this.createApp({
            el: `#${elId}`,
            data: data
        });
    },
    
    ajax(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            },
            body: null
        };
        
        const mergedOptions = {
            ...defaultOptions,
            ...options
        };
        
        if (mergedOptions.body && typeof mergedOptions.body === 'object') {
            mergedOptions.body = JSON.stringify(mergedOptions.body);
        }
        
        return fetch(url, mergedOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('AJAX Error:', error);
                throw error;
            });
    },
    
    showToast(message, type = 'success', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
        toast.style.zIndex = '9999';
        toast.innerHTML = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, duration);
    },
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    formatTime(seconds) {
        if (seconds <= 0) return '00:00';
        
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
    }
};

window.VueUtils = VueUtils;