import os
import sys
import subprocess

def detener_servidor():
    print("🛑 Buscando procesos activos del servidor en el puerto 5000...")
    detenidos = 0

    # Método 1: En Windows usando netstat para encontrar el PID en el puerto 5000
    try:
        output = subprocess.check_output("netstat -ano | findstr :5000", shell=True).decode('utf-8', errors='ignore')
        pids = set()
        for line in output.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 5 and "LISTENING" in parts:
                pid = parts[-1]
                if pid != "0":
                    pids.add(pid)
        
        for pid in pids:
            try:
                subprocess.run(f"taskkill /PID {pid} /F", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(f"✅ Proceso con PID {pid} detenido correctamente.")
                detenidos += 1
            except Exception as e:
                print(f"⚠️ No se pudo detener PID {pid}: {e}")

    except subprocess.CalledProcessError:
        pass
    except Exception as e:
        print(f"Aviso durante la comprobación de red: {e}")

    # Método 2: Encontrar procesos de Python ejecutando start.py
    try:
        wmic_output = subprocess.check_output('wmic process where "name=\'python.exe\'" get processid,commandline', shell=True).decode('utf-8', errors='ignore')
        for line in wmic_output.strip().split('\n'):
            if "start.py" in line or "app.py" in line:
                parts = line.strip().split()
                if parts:
                    pid = parts[-1]
                    if pid.isdigit():
                        try:
                            subprocess.run(f"taskkill /PID {pid} /F", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            print(f"✅ Proceso Python (start.py) con PID {pid} terminado.")
                            detenidos += 1
                        except Exception:
                            pass
    except Exception:
        pass

    if detenidos > 0:
        print(f"\n🎉 Servidor CB Social Hub detenido con éxito ({detenidos} procesos finalizados).")
    else:
        print("\nℹ️ No se encontró ningún servidor en ejecución en el puerto 5000.")

if __name__ == "__main__":
    detener_servidor()

