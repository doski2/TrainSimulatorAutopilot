import { Router } from 'express';
import { SignalingDataService, SignalingData } from '../services/SignalingDataService';

export const apiRoutes = (signalingService: SignalingDataService) => {
  const router = Router();

  // GET /api/status - Estado general del sistema
  router.get('/status', (req, res) => {
    const data = signalingService.getAllData();
    res.json({
      connected: signalingService.isSystemConnected(),
      timestamp: data.timestamp,
      estado_sistema: data.estado_sistema,
      sistemas_activos: data.sistemas_activos
    });
  });

  // GET /api/data - Todos los datos de señalización
  router.get('/data', (req, res) => {
    const data = signalingService.getAllData();
    res.json(data);
  });

  // GET /api/system/:name - Datos específicos de un sistema
  router.get('/system/:name', (req, res) => {
    const { name } = req.params;
    const validSystems = ['acses', 'ptc', 'atc', 'cab'];
    if (validSystems.includes(name)) {
      const systemData = signalingService.getSystemData(name as keyof SignalingData['sistemas_activos']);
      if (systemData) {
        res.json(systemData);
      } else {
        res.status(404).json({ error: `Sistema ${name} no encontrado` });
      }
    } else {
      res.status(400).json({ error: `Sistema inválido. Sistemas válidos: ${validSystems.join(', ')}` });
    }
  });

  // POST /api/command - Enviar comando al sistema
  router.post('/command', (req, res) => {
    try {
      const command = req.body;
      signalingService.sendCommand(command);
      res.json({ success: true, message: 'Comando enviado correctamente' });
    } catch (error) {
      res.status(500).json({ error: 'Error al enviar comando' });
    }
  });

  // GET /api/metrics - Métricas para gráficos
  router.get('/metrics', (req, res) => {
    const data = signalingService.getAllData();
    const metrics = {
      velocidad: {
        actual: data.velocidad_actual,
        maxima: data.velocidad_maxima,
        porcentaje: data.velocidad_maxima > 0 ? (data.velocidad_actual / data.velocidad_maxima) * 100 : 0
      },
      seguridad: {
        freno_emergencia: data.comandos_seguridad.freno_emergencia,
        advertencias: data.advertencias_activas.length,
        estado: data.estado_sistema
      },
      sistemas: Object.entries(data.sistemas_activos).map(([name, active]) => ({
        nombre: name.toUpperCase(),
        activo: active
      }))
    };
    res.json(metrics);
  });

  return router;
};