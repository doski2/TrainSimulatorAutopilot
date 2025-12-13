const { app, BrowserWindow } = require('electron');
const path = require('path');

console.log('🚂 Iniciando Train Simulator Autopilot - Electron');
console.log('📁 Directorio actual:', __dirname);
console.log('🔧 Modo:', process.argv.includes('--dev') ? 'DESARROLLO' : 'PRODUCCIÓN');

function createWindow() {
  console.log('🚂 Creando ventana de Electron...');

  // Crear la ventana del navegador
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false
    },
    icon: path.join(__dirname, 'web/static/img/train-icon.png'), // Opcional: icono de la app
    title: 'Train Simulator Autopilot',
    show: false // No mostrar hasta que esté listo
  });

  console.log('🌐 Intentando cargar URL: http://localhost:5001');

  // Cargar la aplicación web
  const testMode = process.argv.includes('--test');
  const targetUrl = testMode ?
    `file://${__dirname}/test_config.html` :
    'http://localhost:5001';

  console.log('🎯 Modo:', testMode ? 'TEST' : 'NORMAL');
  console.log('🌐 URL objetivo:', targetUrl);

  mainWindow.loadURL(targetUrl).then(() => {
    console.log('✅ URL cargada exitosamente');
    mainWindow.show();
  }).catch((error) => {
    console.error('❌ Error cargando URL:', error);
    // Mostrar error en una página simple
    mainWindow.loadURL(`data:text/html,
      <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
          <h1>Error de conexión</h1>
          <p>No se pudo conectar al servidor web en http://localhost:5001</p>
          <p>Error: ${error.message}</p>
          <p>Asegúrate de que el servidor Flask esté ejecutándose.</p>
          <button onclick="location.reload()">Reintentar</button>
        </body>
      </html>
    `);
    mainWindow.show();
  });

  // Abrir DevTools en desarrollo
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  // Evento cuando la ventana se cierra
  mainWindow.on('closed', () => {
    console.log('🪟 Ventana cerrada');
    // Desreferenciar el objeto window
    mainWindow = null;
  });

  // En modo test, mantener la ventana abierta
  if (testMode) {
    console.log('🧪 Modo test: ventana permanecera abierta para pruebas');
    // No cerrar automáticamente
  }
}

// Este método se llamará cuando Electron haya terminado de inicializarse
app.whenReady().then(() => {
  console.log('⚡ Electron app ready - creando ventana...');
  createWindow();
});

// Salir cuando todas las ventanas estén cerradas
app.on('window-all-closed', () => {
  // En macOS es común que las aplicaciones y su barra de menú
  // permanezcan activas hasta que el usuario salga explícitamente con Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // En macOS es común volver a crear una ventana en la aplicación cuando
  // el icono del dock se hace clic y no hay otras ventanas abiertas
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});