

import socket
import time
import speedtest


def test_kecepatan_dan_throttling():
  print("\n--- ANALISIS KECEPATAN & NET NEUTRALITY (THROTTLING CHECK) ---")
  try:
    st = speedtest.Speedtest()
    print("Mendapatkan server pengujian...")
    servers = st.get_servers()

    # 1. Tes Kecepatan Umum (Baseline)
    print("Menguji kecepatan internet dasar (Baseline)...")
    st.get_best_server()
    dl_speed = st.download() / 1_000_000
    ul_speed = st.upload() / 1_000_000

    print(f"\n[Hasil Baseline]")
    print(f"- Kecepatan Download : {dl_speed:.2f} Mbps")
    print(f"- Kecepatan Upload   : {ul_speed:.2f} Mbps")

    # 2. Simulasi Pengecekan Akses Layanan (Net Neutrality Check)
    print("\nMemeriksa respons koneksi ke beberapa layanan populer...")
    target_layanan = {
        "Google (General Web)": "google.com",
        "YouTube (Streaming)": "googlevideo.com",
        "Netflix (Streaming)": "netflix.com",
        "Cloudflare (DNS/CDN)": "cloudflare.com",
    }

    print("Layanan\t\t\tStatus\t\tLatensi (Ping)")
    print("-" * 50)

    for nama, domain in target_layanan.items():
      start_time = time.time()
      try:
        # Melakukan tes koneksi soket TCP sederhana ke port 443 (HTTPS)
        socket.create_connection((domain, 443), timeout=3)
        latency = (time.time() - start_time) * 1000  # dalam milidetik
        print(f"{nama:<22}\tNormal\t\t{latency:.1f} ms")
      except socket.timeout:
        print(f"{nama:<22}\tRentan/Timeout\t> 3000 ms (Kemungkinan Throttling)")
      except Exception:
        print(f"{nama:<22}\tGagal Akses\t-")

    print("\n[+] Analisis Net Neutrality Selesai.")
    print(
        "[INFO] Jika latensi streaming atau kecepatan unduh turun drastis"
        " dibandingkan baseline tanpa alasan yang jelas, ada indikasi"
        " pembatasan (throttling) oleh ISP."
    )

  except Exception as e:
    print(f"Terjadi kesalahan saat menjalankan analisis: {e}")


if __name__ == "__main__":
  test_kecepatan_dan_throttling()
