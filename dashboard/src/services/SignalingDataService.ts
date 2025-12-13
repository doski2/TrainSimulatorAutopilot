import { spawn } from 'child_process';
import path from 'path';

export interface SignalingData {
  timestamp: number;
  velocidad_actual: number;
  velocidad_maxima: number;
  estado_sistema: string;
  advertencias_activas: string[];
  comandos_seguridad: {
    freno_emergencia: boolean;
    advertencia_sonora: boolean;
    advertencia_visual: boolean;
  };
  sistemas_activos: {
    acses: boolean;
    ptc: boolean;
    atc: boolean;
    cab: boolean;
  };
  datos_por_sistema: {
    acses?: any;
    ptc?: any;
    atc?: any;
    cab?: any;
  };
}

export class SignalingDataService {
  private data: SignalingData;
  private pythonProcess: any = null;
  private isConnected: boolean = false;

  constructor() {
    this.data = this.getDefaultData();
    this.initializePythonConnection();
  }

  private getDefaultData(): SignalingData {
    return {
      timestamp: Date.now(),
      velocidad_actual: 0,
      velocidad_maxima: 0,
      estado_sistema: 'INACTIVO',
      advertencias_activas: [],
      comandos_seguridad: {
        freno_emergencia: false,
        advertencia_sonora: false,
        advertencia_visual: false
      },
      sistemas_activos: {
        acses: false,
        ptc: false,
        atc: false,
        cab: false
      },
      datos_por_sistema: {}
    };
  }

  private initializePythonConnection(): void {
    try {
      // Ruta al script Python principal
      const pythonScript = path.join(__dirname, '../../../scripts/integrator.py');

      this.pythonProcess = spawn('python', [pythonScript], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: path.join(__dirname, '../../../scripts')
      });

      this.pythonProcess.stdout.on('data', (data: Buffer) => {
        try {
          const receivedData = JSON.parse(data.toString().trim());
          this.updateData(receivedData);
          this.isConnected = true;
        } catch (error) {
          console.error('Error parsing Python data:', error);
        }
      });

      this.pythonProcess.stderr.on('data', (data: Buffer) => {
        console.error('Python process error:', data.toString());
      });

      this.pythonProcess.on('close', (code: number) => {
        console.log(`Python process exited with code ${code}`);
        this.isConnected = false;
        // Intentar reconectar después de un tiempo
        setTimeout(() => this.initializePythonConnection(), 5000);
      });

    } catch (error) {
      console.error('Error initializing Python connection:', error);
    }
  }

  private updateData(newData: any): void {
    this.data = {
      ...this.data,
      ...newData,
      timestamp: Date.now()
    };
  }

  public getAllData(): SignalingData {
    return { ...this.data };
  }

  public getSystemData(systemName: keyof SignalingData['sistemas_activos']): any {
    return this.data.datos_por_sistema[systemName] || null;
  }

  public isSystemConnected(): boolean {
    return this.isConnected;
  }

  public sendCommand(command: any): void {
    if (this.pythonProcess && this.isConnected) {
      try {
        this.pythonProcess.stdin.write(JSON.stringify(command) + '\n');
      } catch (error) {
        console.error('Error sending command to Python:', error);
      }
    }
  }

  public disconnect(): void {
    if (this.pythonProcess) {
      this.pythonProcess.kill();
      this.pythonProcess = null;
      this.isConnected = false;
    }
  }
}