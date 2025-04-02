const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const isDev = process.env.NODE_ENV === 'development'

let mainWindow

console.log('Running in', isDev ? 'development' : 'production', 'mode')

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    })

    // 在开发环境中加载 Vite 开发服务器
    if (isDev) {
        console.log('Loading from development server at http://localhost:3002')
        mainWindow.loadURL('http://localhost:3002')
        mainWindow.webContents.openDevTools()
    } else {
        console.log('Loading from production build')
        mainWindow.loadFile(path.join(__dirname, '../frontend/dist/index.html'))
    }

    mainWindow.on('closed', function () {
        mainWindow = null
    })
}

app.on('ready', createWindow)

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit()
})

app.on('activate', function () {
    if (mainWindow === null) createWindow()
})

// 处理与 Python 后端的通信
ipcMain.on('python-message', (event, data) => {
    // TODO: 实现与 Python 后端的通信
    console.log('Received message from Python:', data)
}) 