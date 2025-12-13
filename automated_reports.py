# automated_reports.py
# Sistema de reportes automáticos para Train Simulator Autopilot

import json
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Importar pandas para análisis de datos
import pandas as pd
import schedule

from alert_system import AlertSystem

# Importar módulos del proyecto
from seaborn_analysis import SeabornAnalysis


@dataclass
class ReportSchedule:
    """Configuración de horario para reportes"""

    name: str
    interval: str  # 'daily', 'weekly', 'monthly'
    time: str  # HH:MM format
    day_of_week: Optional[str] = None  # Para reportes semanales
    enabled: bool = True


class AutomatedReports:
    """Sistema de reportes automáticos"""

    def __init__(self, reports_dir="reports_automaticos", config_file="reports_config.json"):
        self.reports_dir = reports_dir
        self.config_file = config_file
        self.analyzer = SeabornAnalysis(use_tsc_integration=True)
        self.alert_system = AlertSystem()

        # Crear directorio de reportes
        os.makedirs(self.reports_dir, exist_ok=True)

        # Configuración por defecto
        self.default_schedules = [
            ReportSchedule("daily_performance", "daily", "23:00"),
            ReportSchedule("weekly_summary", "weekly", "23:30", "sunday"),
            ReportSchedule("monthly_analysis", "monthly", "23:45"),
        ]

        # Cargar configuración
        self.schedules = self.load_schedules()

        # Estado del sistema
        self.running = False
        self.scheduler_thread = None

        print("Sistema de reportes automáticos inicializado")

    def load_schedules(self) -> List[ReportSchedule]:
        """Cargar configuración de horarios"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    data = json.load(f)
                    return [ReportSchedule(**item) for item in data.get("schedules", [])]
            except Exception as e:
                print(f"Error cargando configuración de reportes: {e}")

        return self.default_schedules.copy()

    def save_schedules(self):
        """Guardar configuración de horarios"""
        try:
            data = {
                "schedules": [vars(schedule) for schedule in self.schedules],
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Configuración de reportes guardada en {self.config_file}")
        except Exception as e:
            print(f"Error guardando configuración: {e}")

    def generate_daily_performance_report(self) -> str:
        """Generar reporte diario de rendimiento"""
        print("📊 Generando reporte diario de rendimiento...")

        # Crear subdirectorio para el día
        today = datetime.now().strftime("%Y-%m-%d")
        report_dir = os.path.join(self.reports_dir, f"daily_{today}")
        os.makedirs(report_dir, exist_ok=True)

        try:
            # Recopilar datos del último día
            if self.analyzer.load_data_from_tsc(
                max_records=1000, collection_time=60
            ):  # 1 minuto de datos
                # Generar análisis completo
                self.analyzer.generate_complete_report(report_dir)

                # Agregar información específica del reporte diario
                daily_info = self._generate_daily_summary(report_dir)

                # Guardar información del reporte
                info_file = os.path.join(report_dir, "daily_report_info.json")
                with open(info_file, "w", encoding="utf-8") as f:
                    json.dump(daily_info, f, indent=2, ensure_ascii=False)

                print(f"✅ Reporte diario generado: {report_dir}")
                return report_dir
            else:
                print("❌ No se pudieron recopilar datos para reporte diario")
                return ""

        except Exception as e:
            print(f"❌ Error generando reporte diario: {e}")
            return ""

    def generate_weekly_summary_report(self) -> str:
        """Generar reporte semanal resumen"""
        print("📈 Generando reporte semanal resumen...")

        # Crear subdirectorio para la semana
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())  # Lunes de esta semana
        week_str = week_start.strftime("%Y-%W")  # Formato año-semana
        report_dir = os.path.join(self.reports_dir, f"weekly_{week_str}")
        os.makedirs(report_dir, exist_ok=True)

        try:
            # Recopilar datos de la semana (más tiempo de recopilación)
            if self.analyzer.load_data_from_tsc(max_records=5000, collection_time=300):  # 5 minutos
                # Generar análisis completo
                self.analyzer.generate_complete_report(report_dir)

                # Agregar análisis semanal específico
                weekly_info = self._generate_weekly_summary(report_dir)

                # Guardar información del reporte
                info_file = os.path.join(report_dir, "weekly_report_info.json")
                with open(info_file, "w", encoding="utf-8") as f:
                    json.dump(weekly_info, f, indent=2, ensure_ascii=False)

                print(f"✅ Reporte semanal generado: {report_dir}")
                return report_dir
            else:
                print("❌ No se pudieron recopilar datos para reporte semanal")
                return ""

        except Exception as e:
            print(f"❌ Error generando reporte semanal: {e}")
            return ""

    def generate_monthly_analysis_report(self) -> str:
        """Generar reporte mensual de análisis detallado"""
        print("📊 Generando reporte mensual de análisis...")

        # Crear subdirectorio para el mes
        today = datetime.now()
        month_str = today.strftime("%Y-%m")
        report_dir = os.path.join(self.reports_dir, f"monthly_{month_str}")
        os.makedirs(report_dir, exist_ok=True)

        try:
            # Recopilar datos del mes (recopilación más larga)
            if self.analyzer.load_data_from_tsc(
                max_records=10000, collection_time=600
            ):  # 10 minutos
                # Generar análisis completo
                self.analyzer.generate_complete_report(report_dir)

                # Agregar análisis mensual específico
                monthly_info = self._generate_monthly_analysis(report_dir)

                # Guardar información del reporte
                info_file = os.path.join(report_dir, "monthly_report_info.json")
                with open(info_file, "w", encoding="utf-8") as f:
                    json.dump(monthly_info, f, indent=2, ensure_ascii=False)

                print(f"✅ Reporte mensual generado: {report_dir}")
                return report_dir
            else:
                print("❌ No se pudieron recopilar datos para reporte mensual")
                return ""

        except Exception as e:
            print(f"❌ Error generando reporte mensual: {e}")
            return ""

    def _generate_daily_summary(self, report_dir: str) -> Dict:
        """Generar resumen específico del día"""
        summary = {
            "report_type": "daily_performance",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "generated_at": datetime.now().isoformat(),
            "data_points": len(self.analyzer.df) if self.analyzer.df is not None else 0,
            "alerts_summary": self.alert_system.get_alerts_summary(),
        }

        if self.analyzer.df is not None and "velocidad" in self.analyzer.df.columns:
            vel_stats = self.analyzer.df["velocidad"].describe()
            summary["velocity_stats"] = {
                "mean": float(vel_stats["mean"]),
                "max": float(vel_stats["max"]),
                "min": float(vel_stats["min"]),
                "std": float(vel_stats["std"]),
            }

            # Calcular tiempo por rangos de velocidad
            vel_ranges = pd.cut(
                self.analyzer.df["velocidad"],
                bins=[0, 20, 40, 60, 80, 100, 200],
                labels=["0-20", "20-40", "40-60", "60-80", "80-100", "100+"],
            )
            range_counts = vel_ranges.value_counts().to_dict()
            summary["velocity_ranges"] = {str(k): int(v) for k, v in range_counts.items()}

        return summary

    def _generate_weekly_summary(self, report_dir: str) -> Dict:
        """Generar resumen específico de la semana"""
        summary = {
            "report_type": "weekly_summary",
            "week": datetime.now().strftime("%Y-%W"),
            "generated_at": datetime.now().isoformat(),
            "data_points": len(self.analyzer.df) if self.analyzer.df is not None else 0,
            "alerts_summary": self.alert_system.get_alerts_summary(),
        }

        if self.analyzer.df is not None:
            # Análisis por día de la semana
            if "fecha_hora" in self.analyzer.df.columns:
                # Use apply() to call `day_name` on Timestamp objects to avoid
                # static analysis warnings for pandas .dt accessor
                self.analyzer.df["day_of_week"] = self.analyzer.df["fecha_hora"].apply(
                    lambda x: x.day_name() if hasattr(x, "day_name") else str(x)
                )
                daily_stats = {}

                for day in [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]:
                    day_data = self.analyzer.df[self.analyzer.df["day_of_week"] == day]
                    if not day_data.empty and "velocidad" in day_data.columns:
                        daily_stats[day] = {
                            "count": len(day_data),
                            "avg_velocity": float(day_data["velocidad"].mean()),
                            "max_velocity": float(day_data["velocidad"].max()),
                        }

                summary["daily_stats"] = daily_stats

        return summary

    def _generate_monthly_analysis(self, report_dir: str) -> Dict:
        """Generar análisis específico del mes"""
        summary = {
            "report_type": "monthly_analysis",
            "month": datetime.now().strftime("%Y-%m"),
            "generated_at": datetime.now().isoformat(),
            "data_points": len(self.analyzer.df) if self.analyzer.df is not None else 0,
            "alerts_summary": self.alert_system.get_alerts_summary(),
        }

        if self.analyzer.df is not None:
            # Tendencias mensuales
            if "fecha_hora" in self.analyzer.df.columns and "velocidad" in self.analyzer.df.columns:
                # Agrupar por día
                # Use apply() to extract date to avoid static type issues
                daily_avg = self.analyzer.df.groupby(self.analyzer.df["fecha_hora"].apply(
                    lambda x: x.date()
                ))[
                    "velocidad"
                ].mean()
                summary["daily_velocity_trend"] = {
                    str(date): float(avg) for date, avg in daily_avg.items()
                }

                # Estadísticas mensuales
                summary["monthly_stats"] = {
                    "total_sessions": len(daily_avg),
                    "avg_daily_velocity": float(daily_avg.mean()),
                    "best_day": str(daily_avg.idxmax()),
                    "worst_day": str(daily_avg.idxmin()),
                }

        return summary

    def schedule_reports(self):
        """Programar todos los reportes según la configuración"""
        # Limpiar schedule anterior
        schedule.clear()

        for sched in self.schedules:
            if not sched.enabled:
                continue

            if sched.interval == "daily":
                schedule.every().day.at(sched.time).do(self._run_daily_report)
                print(f"📅 Reporte diario programado: {sched.time}")

            elif sched.interval == "weekly":
                if sched.day_of_week:
                    day_map = {
                        "monday": schedule.every().monday,
                        "tuesday": schedule.every().tuesday,
                        "wednesday": schedule.every().wednesday,
                        "thursday": schedule.every().thursday,
                        "friday": schedule.every().friday,
                        "saturday": schedule.every().saturday,
                        "sunday": schedule.every().sunday,
                    }

                    if sched.day_of_week.lower() in day_map:
                        day_map[sched.day_of_week.lower()].at(sched.time).do(
                            self._run_weekly_report
                        )
                        print(f"📅 Reporte semanal programado: {sched.day_of_week} {sched.time}")

            elif sched.interval == "monthly":
                # Para simplificar, ejecutar el primer día del mes
                schedule.every().day.at(sched.time).do(self._run_monthly_report).tag("monthly")
                print(f"📅 Reporte mensual programado: {sched.time} (primer día del mes)")

    def _run_daily_report(self):
        """Wrapper para ejecutar reporte diario"""
        try:
            result = self.generate_daily_performance_report()
            if result:
                print(f"✅ Reporte diario completado: {result}")
            else:
                print("❌ Reporte diario falló")
        except Exception as e:
            print(f"❌ Error en reporte diario: {e}")

    def _run_weekly_report(self):
        """Wrapper para ejecutar reporte semanal"""
        try:
            result = self.generate_weekly_summary_report()
            if result:
                print(f"✅ Reporte semanal completado: {result}")
            else:
                print("❌ Reporte semanal falló")
        except Exception as e:
            print(f"❌ Error en reporte semanal: {e}")

    def _run_monthly_report(self):
        """Wrapper para ejecutar reporte mensual (solo primer día del mes)"""
        if datetime.now().day == 1:  # Solo primer día del mes
            try:
                result = self.generate_monthly_analysis_report()
                if result:
                    print(f"✅ Reporte mensual completado: {result}")
                else:
                    print("❌ Reporte mensual falló")
            except Exception as e:
                print(f"❌ Error en reporte mensual: {e}")

    def start_automation(self):
        """Iniciar sistema de automatización"""
        if self.running:
            print("Sistema de automatización ya está ejecutándose")
            return

        print("🚀 Iniciando sistema de reportes automáticos...")

        # Programar reportes
        self.schedule_reports()

        # Iniciar hilo del scheduler
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()

        print("✅ Sistema de automatización iniciado")

    def stop_automation(self):
        """Detener sistema de automatización"""
        self.running = False
        schedule.clear()
        print("🛑 Sistema de automatización detenido")

    def _run_scheduler(self):
        """Ejecutar el scheduler en bucle"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
            except Exception as e:
                print(f"Error en scheduler: {e}")
                time.sleep(60)

    def run_manual_report(self, report_type: str) -> str:
        """Ejecutar reporte manualmente"""
        if report_type == "daily":
            return self.generate_daily_performance_report()
        elif report_type == "weekly":
            return self.generate_weekly_summary_report()
        elif report_type == "monthly":
            return self.generate_monthly_analysis_report()
        else:
            print(f"Tipo de reporte desconocido: {report_type}")
            return ""

    def get_reports_status(self) -> Dict:
        """Obtener estado del sistema de reportes"""
        reports_count = {}
        total_size = 0

        if os.path.exists(self.reports_dir):
            for root, _, files in os.walk(self.reports_dir):
                for file in files:
                    if file.endswith((".png", ".html", ".txt", ".json")):
                        total_size += os.path.getsize(os.path.join(root, file))

            # Contar por tipo
            for item in os.listdir(self.reports_dir):
                if os.path.isdir(os.path.join(self.reports_dir, item)):
                    if item.startswith("daily_"):
                        reports_count["daily"] = reports_count.get("daily", 0) + 1
                    elif item.startswith("weekly_"):
                        reports_count["weekly"] = reports_count.get("weekly", 0) + 1
                    elif item.startswith("monthly_"):
                        reports_count["monthly"] = reports_count.get("monthly", 0) + 1

        return {
            "automation_running": self.running,
            "reports_directory": self.reports_dir,
            "total_reports": sum(reports_count.values()),
            "reports_by_type": reports_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "schedules": [vars(s) for s in self.schedules],
            "next_runs": self._get_next_runs(),
        }

    def _get_next_runs(self) -> Dict:
        """Obtener próximos horarios de ejecución"""
        next_runs = {}

        for sched in self.schedules:
            if sched.enabled:
                try:
                    if sched.interval == "daily":
                        # Calcular próximo daily
                        today = datetime.now().date()
                        next_time = datetime.combine(
                            today, datetime.strptime(sched.time, "%H:%M").time()
                        )
                        if next_time <= datetime.now():
                            next_time += timedelta(days=1)
                        next_runs[sched.name] = next_time.isoformat()

                    elif sched.interval == "weekly" and sched.day_of_week:
                        # Calcular próximo semanal
                        day_names = [
                            "monday",
                            "tuesday",
                            "wednesday",
                            "thursday",
                            "friday",
                            "saturday",
                            "sunday",
                        ]
                        target_day = day_names.index(sched.day_of_week.lower())

                        today = datetime.now()
                        days_ahead = (target_day - today.weekday()) % 7
                        if (
                            days_ahead == 0
                            and datetime.combine(
                                today.date(), datetime.strptime(sched.time, "%H:%M").time()
                            )
                            <= today
                        ):
                            days_ahead = 7

                        next_time = today + timedelta(days=days_ahead)
                        next_time = datetime.combine(
                            next_time.date(), datetime.strptime(sched.time, "%H:%M").time()
                        )
                        next_runs[sched.name] = next_time.isoformat()

                except Exception as e:
                    print(f"Error calculando próximo {sched.name}: {e}")

        return next_runs


# Funciones de utilidad para integración
def get_automated_reports() -> AutomatedReports:
    """Obtener instancia singleton del sistema de reportes"""
    if not hasattr(get_automated_reports, "_instance"):
        get_automated_reports._instance = AutomatedReports()
    return get_automated_reports._instance


def generate_report(report_type: str) -> Dict:
    """Generar reporte manualmente (llamada desde web dashboard)"""
    system = get_automated_reports()
    result_path = system.run_manual_report(report_type)

    return {
        "success": bool(result_path),
        "report_type": report_type,
        "path": result_path,
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    print("Sistema de Reportes Automáticos - Train Simulator Autopilot")
    print("=" * 60)

    # Crear sistema de reportes
    reports_system = AutomatedReports()

    # Mostrar estado actual
    status = reports_system.get_reports_status()
    print(f"📁 Directorio de reportes: {status['reports_directory']}")
    print(f"📊 Reportes totales: {status['total_reports']}")
    print(f"💾 Espacio usado: {status['total_size_mb']} MB")

    # Generar reporte de ejemplo
    print("\n🧪 Generando reporte diario de ejemplo...")
    result = reports_system.run_manual_report("daily")

    if result:
        print(f"✅ Reporte generado exitosamente: {result}")
    else:
        print("❌ Error generando reporte")

    # Mostrar próximos horarios
    print("\n📅 Próximos reportes programados:")
    next_runs = status["next_runs"]
    if next_runs:
        for name, next_time in next_runs.items():
            print(f"  {name}: {next_time}")
    else:
        print("  Ningún reporte programado")

    print("\n💡 Para iniciar automatización completa, usar: reports_system.start_automation()")
