const { contextBridge, ipcRenderer } = require('electron')

// 暴露安全的 API 到渲染进程
contextBridge.exposeInMainWorld('electron', {
    // 发送消息到主进程
    sendMessage: (channel, data) => {
        ipcRenderer.send(channel, data)
    },

    // 接收主进程消息
    onMessage: (channel, func) => {
        ipcRenderer.on(channel, (event, ...args) => func(...args))
    },

    // 移除消息监听
    removeListener: (channel, func) => {
        ipcRenderer.removeListener(channel, func)
    }
}) 