$mappings = @(
    @{ src = "templates\staff\BaoCaoThongKe"; dest = "BaoCaoThongKe\templates\staff" },
    @{ src = "templates\staff\QuanLyDanhMuc"; dest = "QuanLyDanhMuc\templates\staff" },
    @{ src = "templates\staff\quanLyDonHang"; dest = "quanLyDonHang\templates\staff" },
    @{ src = "templates\staff\quanLyKhachHang"; dest = "quanLyKhachHang\templates\staff" },
    @{ src = "templates\staff\QuanLyKhuyenMai"; dest = "QuanLyKhuyenMai\templates\staff" },
    @{ src = "templates\staff\QuanLyNhaCungCap"; dest = "QuanLyNhaCungCap\templates\staff" },
    @{ src = "templates\staff\QuanLyNhapHang"; dest = "QuanLyNhapHang\templates\staff" },
    @{ src = "templates\staff\quanLySanPham"; dest = "quanLySanPham\templates\staff" },
    @{ src = "templates\user\donDat"; dest = "donDat\templates\user" },
    @{ src = "templates\user\gioHang"; dest = "gioHang\templates\user" }
)

foreach ($map in $mappings) {
    if (Test-Path $map.src) {
        New-Item -ItemType Directory -Force -Path $map.dest | Out-Null
        Move-Item -Path $map.src -Destination $map.dest -Force
        Write-Host "Moved $($map.src) to $($map.dest)"
    } else {
        Write-Host "Not found $($map.src)"
    }
}
