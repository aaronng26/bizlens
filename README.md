# BizLens – OCBC

Streamlit app untuk melihat potensi kota dan cabang OCBC. Semua file ada di satu folder (tanpa subfolder),
dan **semua data dibaca langsung dari `biz_lens_data.xlsx`**.

## Isi folder

| File | Fungsi |
|---|---|
| `app.py` | Entry point + navigasi |
| `home.py` | Halaman BizLens (ringkasan, 360 Assessment, sebaran wilayah) |
| `city_profile.py` | Halaman City Profile |
| `branch_profile.py` | Halaman Branch Profile |
| `styling.py` | Theme OCBC merah-putih |
| `bizlens_data.py` | Membaca & menyusun data dari Excel |
| `biz_lens_data.xlsx` | **Semua data ada di sini** |
| `requirements.txt` | Library yang dibutuhkan |
| `.python-version` | Versi Python (3.11) |

## Jalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Update data

1. Buka `biz_lens_data.xlsx`, edit atau tambah baris, lalu **Save**
2. Refresh halaman app di browser

App otomatis membaca ulang Excel setiap kali file disimpan. Tidak perlu menjalankan script apa pun.

Kalau di Streamlit Cloud: upload `biz_lens_data.xlsx` yang baru ke GitHub, app akan ikut terbarui.

## Isi sheet Excel

| Sheet | Isi |
|---|---|
| `info` | Periode data (`periode`, mis. EOY 2025) dan definisi area layanan MPS (`area_layanan`) |
| `cities` | 1 baris per kota |
| `city_dims` | Skor 5 dimensi per kota (slug, dimensi, skor) |
| `city_banks` | Jumlah cabang bank per kelompok per kota |
| `branches` | 1 baris per cabang |
| `branch_mpi` | Komponen MPI per cabang |
| `branch_internal` | Tier internal per cabang |
| `branch_nearest` | Cabang terdekat (baris `nama` = nama cabangnya) |
| `branch_context` | Lingkungan sekitar; `kategori` = commercial / competition / demographic / economic |
| `branch_overlap` | Jumlah cabang tetangga per tipe & jarak |
| `neighbors` | Daftar cabang tetangga; `radius_group` = `lt_2km` atau `2_5km` |
| `tier_cps` | Distribusi kota per tier CPS |
| `tier_mps` | Distribusi cabang per tier MPS |
| `regional` | Data per pulau |
| `overlap_heatmap` | Matriks MPS × CPS (360 Assessment) |
| `proposal_cabang` | 3 kategori 360 Assessment |
| `proposal_dist` | Distribusi per tier CPS tiap kategori |
| `proposal_action` | Rekomendasi; `aksi` = close / review |

### Semua angka dihitung dari Excel

Tidak ada angka data yang ditulis di kode. Contohnya:

- Total kota & cabang di homepage = jumlah dari `tier_cps` dan `tier_mps`
- "Prioritas" = dua tier teratas di `tier_cps` / `tier_mps` (diurutkan dari angka di nama tier)
- Isi, label baris/kolom, warna, dan legend heatmap = dari `overlap_heatmap` + `proposal_cabang`
- Insight wilayah = dihitung dari `regional` (CPS tertinggi, kota belum digarap terbanyak, CPS terendah)
- Garis acuan di radar & bar chart = batas tier teratas di kolom `rentang` (`tier_cps` untuk kota, `tier_mps` untuk cabang)
- Periode data di judul & bawah halaman = sheet `info`

### Aturan penting

- **Jangan ganti nama sheet atau nama kolom.** Kolom tambahan boleh, tidak akan mengganggu.
- `slug` adalah ID unik tanpa spasi (contoh: `kota_surabaya`, `bandung_dago`). Slug yang sama
  dipakai untuk menghubungkan antar sheet, misalnya `kota_bandung` di `cities`, `city_dims`, dan `city_banks`.
- Sel boleh kosong; app akan menampilkan "–".
- Angka persen ditulis sebagai desimal: `0.59` untuk 59%.
- Kalau ada yang salah format, app menampilkan pesan merah yang menyebut sheet/kolom mana yang bermasalah.
- Tutup Excel sebelum menjalankan app di laptop yang sama kalau muncul error "tidak bisa dibuka".

---

© OCBC NISP · BizLens 2026
