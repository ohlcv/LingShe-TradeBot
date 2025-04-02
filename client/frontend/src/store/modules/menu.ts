import { defineStore } from 'pinia';
import { ref } from 'vue';

// 定义菜单状态管理
export const useMenuStore = defineStore('menu', () => {
    // 当前选中的菜单项
    const selectedKeys = ref<string[]>(['dashboard']);

    // 设置当前选中的菜单项
    const setSelectedKeys = (keys: string[]) => {
        selectedKeys.value = keys;
    };

    // 根据路径更新选中菜单
    const updateSelectedKeysByPath = (path: string) => {
        const pathParts = path.split('/');
        const mainPath = pathParts[1] || 'dashboard';

        if (mainPath === 'strategies') {
            selectedKeys.value = ['strategy-list'];
        } else {
            selectedKeys.value = [mainPath];
        }
    };

    return {
        selectedKeys,
        setSelectedKeys,
        updateSelectedKeysByPath
    };
}); 