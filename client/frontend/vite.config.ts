import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import Components from 'unplugin-vue-components/vite'
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers'
import { createStyleImportPlugin, AndDesignVueResolve } from 'vite-plugin-style-import'

// 获取项目根目录绝对路径
const srcRoot = path.resolve(__dirname, 'src')

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        Components({
            // 自动导入组件
            resolvers: [
                AntDesignVueResolver({
                    importStyle: false, // 不自动导入样式，改为在main.ts中手动导入
                }),
            ],
            // 指定组件位置，默认是src/components
            dirs: ['src/components'],
            // 组件的有效文件扩展名
            extensions: ['vue'],
            // 搜索子目录
            deep: true,
            // 生成类型声明文件
            dts: true,
        }),
        createStyleImportPlugin({
            resolves: [
                AndDesignVueResolve()
            ],
            // 自定义规则
            libs: [
                {
                    libraryName: 'ant-design-vue',
                    esModule: true,
                    resolveStyle: (name) => `ant-design-vue/es/${name}/style/index`
                }
            ]
        })
    ],
    base: './',
    resolve: {
        alias: {
            '@': srcRoot,
        },
    },
    css: {
        preprocessorOptions: {
            less: {
                javascriptEnabled: true, // 启用Less的JavaScript功能
                modifyVars: {
                    // 导入自定义主题文件
                    hack: `true; @import "${path.resolve(srcRoot, 'theme.less')}";`,
                },
            },
        },
    },
    server: {
        port: 3003,
        strictPort: false,
        proxy: {
            '/api': {
                target: 'http://localhost:8080',
                changeOrigin: true,
                // 保留/api路径
                rewrite: (pathStr) => pathStr
            },
        },
    },
    build: {
        outDir: 'dist',
        assetsDir: 'assets',
        emptyOutDir: true,
    },
})
