import json

from django.db import transaction
from django.db.models import Max, Q
from django.http import JsonResponse
from django.shortcuts import render

from QuanLyNhapHang.models import ChiTietNhapHang, NhapHang
from QuanLyNhaCungCap.models import NhaCungCap
from quanLySanPham.models import BienTheSanPham, SanPham


def nhap_hang_view(request):
    ma_search = request.GET.get("ma_search", "").strip()
    ncc_search = request.GET.get("ncc_search", "").strip()
    ngay_search = request.GET.get("ngay_search", "").strip()

    don_nhaps = NhapHang.objects.select_related("NCC_Ma").all()
    if ma_search:
        don_nhaps = don_nhaps.filter(NH_Ma__icontains=ma_search)
    if ncc_search:
        don_nhaps = don_nhaps.filter(NCC_Ma__NCC_Ten__icontains=ncc_search)
    if ngay_search:
        don_nhaps = don_nhaps.filter(NH_Ngay=ngay_search)

    context = {
        "ds_nhap_hang": don_nhaps.order_by("NH_Ma"),
        "nha_cung_cap": NhaCungCap.objects.all(),
        "san_pham": SanPham.objects.all(),
        "ma_search": ma_search,
        "ncc_search": ncc_search,
        "ngay_search": ngay_search,
    }
    return render(request, "QuanLyNhapHang/QuanLyNhapHang.html", context)


def get_variants(request):
    """
    API lay danh sach bien the (size, mau) dua tren ma san pham chung.
    Kem theo gia ban cua san pham de lam mac dinh cho gia nhap.
    """
    sp_ma = request.GET.get("sp_ma")
    if sp_ma:
        try:
            sp = SanPham.objects.get(SP_Ma=sp_ma)
            variants_qs = BienTheSanPham.objects.filter(SP_Ma_id=sp_ma).values(
                "BTSP_Ma", "SP_KichThuoc", "SP_MauSac"
            )
            return JsonResponse(
                {"variants": list(variants_qs), "sp_gia_ban": float(sp.SP_GiaBan)},
                safe=False,
            )
        except SanPham.DoesNotExist:
            pass
    return JsonResponse({"variants": [], "sp_gia_ban": 0}, safe=False)


@transaction.atomic
def add_nhap_hang(request):
    """
    Xu ly luu don nhap hang, chi tiet don nhap va cap nhat ton kho vao bang BienThe.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            last_import = NhapHang.objects.all().aggregate(Max("NH_Ma"))["NH_Ma__max"]
            if last_import and last_import.startswith("NH"):
                try:
                    last_num = int(last_import[2:])
                    new_num = last_num + 1
                except ValueError:
                    new_num = 1
            else:
                new_num = 1

            ma_dn = f"NH{new_num:07d}"

            ncc = NhaCungCap.objects.get(NCC_Ma=data["ncc_ma"])
            don_nhap = NhapHang.objects.create(
                NH_Ma=ma_dn,
                NCC_Ma=ncc,
                NH_TongTien=data["tong_tien"],
            )

            for item in data["items"]:
                btsp = BienTheSanPham.objects.get(BTSP_Ma=item["btsp_ma"])
                ChiTietNhapHang.objects.create(
                    NH_Ma=don_nhap,
                    BTSP_Ma=btsp,
                    NH_DonGia=item["don_gia"],
                    NH_SL=item["so_luong"],
                    NH_TTien=item["thanh_tien"],
                )

                btsp.SP_SL += int(item["so_luong"])
                btsp.save()

            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Da tao thanh cong don nhap hang: {ma_dn}",
                }
            )
        except NhaCungCap.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Nha cung cap khong ton tai!"},
                status=400,
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse(
        {"status": "error", "message": "Yeu cau khong hop le!"},
        status=405,
    )


def delete_nhap_hang(request, ma_dn):
    if request.method == "POST":
        try:
            don_nhap = NhapHang.objects.get(NH_Ma=ma_dn)

            chi_tiets = ChiTietNhapHang.objects.filter(NH_Ma=don_nhap)
            for ct in chi_tiets:
                btsp = ct.BTSP_Ma
                btsp.SP_SL -= ct.NH_SL
                btsp.save()

            don_nhap.delete()

            return JsonResponse(
                {"status": "success", "message": "Da xoa don nhap thanh cong!"}
            )
        except NhapHang.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Don nhap khong ton tai!"},
                status=404,
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)


def get_detail_nhap_hang(request, ma_dn):
    try:
        don_nhap = NhapHang.objects.get(NH_Ma=ma_dn)
        chi_tiets = ChiTietNhapHang.objects.filter(NH_Ma=don_nhap).select_related(
            "BTSP_Ma__SP_Ma"
        )

        item_list = []
        for ct in chi_tiets:
            item_list.append(
                {
                    "ten_sp": ct.BTSP_Ma.SP_Ma.SP_Ten,
                    "mau_sac": ct.BTSP_Ma.SP_MauSac,
                    "kich_thuoc": ct.BTSP_Ma.SP_KichThuoc,
                    "so_luong": ct.NH_SL,
                    "don_gia": float(ct.NH_DonGia),
                    "thanh_tien": float(ct.NH_TTien),
                }
            )

        data = {
            "ma_dn": don_nhap.NH_Ma,
            "ncc_ten": don_nhap.NCC_Ma.NCC_Ten,
            "ncc_ma": don_nhap.NCC_Ma.NCC_Ma,
            "ngay_nhap": don_nhap.NH_Ngay.strftime("%d-%m-%Y") if don_nhap.NH_Ngay else None,
            "tong_tien": float(don_nhap.NH_TongTien),
            "items": item_list,
        }
        return JsonResponse(data)
    except NhapHang.DoesNotExist:
        return JsonResponse({"error": "Khong tim thay don hang"}, status=404)
