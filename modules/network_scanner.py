import subprocess as sb
import re
import speedtest as sp
import time
import socket as sc

class NetworkDiagnostics:
    def __init__(self):
        # Atribut untuk menyimpan state / hasil pengecekan
        self.ssid = "Tidak terhubung"
        self.signal = "N/A"
        self.throttling_results = {}
        self.ping = 0.0
        self.download_speed = 0.0
        self.upload_speed = 0.0

    def check_wifi_status(self):
        """Metode untuk mengambil informasi Wi-Fi lokal menggunakan subprocess & re"""
        try:
            output = sb.check_output(['netsh', 'wlan', 'show', 'interfaces']).decode('utf-8', errors="backslashreplace")
            
            ssid_match = re.search(r"SSID\s*:\s*(.+)", output)
            signal_match = re.search(r"Signal\s*:\s*(\d+)%", output)
            
            if ssid_match:
                self.ssid = ssid_match.group(1).strip()
            if signal_match:
                self.signal = signal_match.group(1) + "%"
        except Exception:
            # Jika perintah gagal (misal bukan Windows atau tidak ada adapter Wi-Fi)
            pass
        
        return self.ssid, self.signal

    def run_speedtest(self):
        """Metode untuk mengukur kecepatan internet menggunakan modul speedtest"""
        if sp is None:
            print("Peringatan: Modul speedtest belum diinstal. Jalankan: pip install speedtest-cli")
            return False

        print("Menghubungkan ke server Speedtest...")
        try:
            st = sp.Speedtest()
            st.get_best_server()
            
            print("Mengukur kecepatan Download & Upload...")
            self.ping = st.results.ping
            self.download_speed = st.download() / 1_000_000  # Mbps
            self.upload_speed = st.upload() / 1_000_000      # Mbps
            return True
        except Exception as e:
            print(f"Gagal melakukan speedtest: {e}")
            return False
    
    def check_throttling(self):
        """Meteode pengecekan Throttling"""
        print("\nMemeriksa respons koneksi ke beberapa layanan populer...")
        target_layanan = {
                                "Google (General Web)": "google.com",
                                "YouTube (Streaming)": "googlevideo.com",
                                "Netflix (Streaming)": "netflix.com",
                                "Cloudflare (DNS/CDN)": "cloudflare.com",
                            }
                        
        for nama, domain in target_layanan.items():
            start_time = time.time()
            try:
                # Tes koneksi soket TCP ke port 443 (HTTPS) dengan timeout 3 detik
                sc.create_connection((domain, 443), timeout=3)
                latency = (time.time() - start_time) * 1000  # dalam milidetik
                
                # Tentukan status berdasarkan latensi (misal > 1500 ms diindikasikan lambat)
                status = "Lambat (Indikasi)" if latency > 1500 else "Normal"
                
                # Simpan ke dictionary hasil
                self.throttling_results[nama] = {
                    "status": status,
                    "latency": latency
                }
            except sc.timeout:
                self.throttling_results[nama] = {
                    "status": "Timeout / Rentan",
                    "latency": "> 3000 ms"
                }
            except Exception:
                self.throttling_results[nama] = {
                    "status": "Gagal Akses",
                    "latency": "-"
                }

    def display_results(self):
        """Metode untuk mencetak seluruh hasil diagnostik"""
        print("\n" + "="*35)
        print("     HASIL DIAGNOSTIK JARINGAN")
        print("="*35)
        print(f"Nama Wi-Fi (SSID) : {self.ssid}")
        print(f"Kekuatan Sinyal   : {self.signal}")
        if sp:
            print(f"Ping              : {self.ping:.2f} ms")
            print(f"Kecepatan Download: {self.download_speed:.2f} Mbps")
            print(f"Kecepatan Upload  : {self.upload_speed:.2f} Mbps")
        print("="*60)
        print("Layanan\t\t\t\tStatus\t\tLatensi (Ping)")
        print("=" * 60)

        for nama, data in self.throttling_results.items():
            lat = data["latency"]
            lat_str = f"{lat:.1f} ms" if isinstance(lat, float) else lat
            print(f"{nama:<25} | {data['status']:<18} | {lat_str}")

        print("\n[+] Analisis Net Neutrality Selesai.")
        print(
            "[INFO] Jika latensi streaming atau kecepatan unduh turun drastis"
            " dibandingkan baseline tanpa alasan yang jelas, ada indikasi"
            " pembatasan (throttling) oleh ISP."
            )       

# --- Bagian Eksekusi Program ---
if __name__ == "__main__":
    # 1. Inisialisasi Objek dari Class NetworkDiagnostics
    diagnostic = NetworkDiagnostics()
    
    # 2. Menjalankan proses pengecekan Wi-Fi lokal
    print("Mendeteksi status Wi-Fi lokal...")
    diagnostic.check_wifi_status()
    
    # 3. Menjalankan speedtest internet
    diagnostic.run_speedtest()

    # 4. Menjalankan throttling
    diagnostic.check_throttling()

    # 5. Menampilkan hasil akhir
    diagnostic.display_results()

    
