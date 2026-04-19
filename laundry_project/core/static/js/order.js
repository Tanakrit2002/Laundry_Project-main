let total = 0;
let cartArray = [];

function updateFabricOptions() {
    const type = document.getElementById('serviceTypeSelect').value;
    const fabricSelect = document.getElementById('fabricSelect');
    const unitSelect = document.getElementById('unitSelect');
    const priceDisplay = document.getElementById('priceDisplay');
    
    fabricSelect.innerHTML = '<option value="">-- เลือกชนิดผ้า --</option>';
    priceDisplay.value = "0.00";
    
    if (!type) {
        unitSelect.value = "-";
        return;
    }

    const filteredServices = rawServices.filter(item => item.type === type);
    if (filteredServices.length > 0) {
        unitSelect.value = filteredServices[0].unit; // อัปเดตหน่วยรอทันที

        filteredServices.forEach(srv => {
            let opt = document.createElement('option');
            opt.value = srv.id; 
            opt.setAttribute('data-price', srv.price);
            opt.setAttribute('data-name', srv.type + ' - ' + srv.fabric);
            opt.setAttribute('data-unit', srv.unit);
            opt.textContent = srv.fabric;
            fabricSelect.appendChild(opt);
        });
    } else {
        unitSelect.value = "-";
    }
}

function updatePrice() {
    const fabricSelect = document.getElementById('fabricSelect');
    const unitSelect = document.getElementById('unitSelect');
    const priceDisplay = document.getElementById('priceDisplay');

    if (fabricSelect.value === "") {
        priceDisplay.value = "0.00";
        return;
    }
    
    const option = fabricSelect.options[fabricSelect.selectedIndex];
    priceDisplay.value = parseFloat(option.getAttribute('data-price')).toFixed(2);
    unitSelect.value = option.getAttribute('data-unit'); // ล็อกหน่วยเป๊ะๆ
}

function addItem() {
    const customerSelect = document.getElementById('customerSelect') ? document.getElementById('customerSelect').value : 'has_id';
    const newCusName = document.getElementById('newCusName') ? document.getElementById('newCusName').value.trim() : 'has_name';
    const newCusPhone = document.getElementById('newCusPhone') ? document.getElementById('newCusPhone').value.trim() : 'has_phone';

    if (!customerSelect && (!newCusName || !newCusPhone)) {
        Swal.fire({
            icon: 'warning',
            title: 'ข้อมูลลูกค้าไม่ครบถ้วน',
            text: 'กรุณาเลือกหรือกรอกชื่อและเบอร์โทรลูกค้าก่อนเพิ่มรายการผ้านะจ๊ะ',
            confirmButtonColor: '#0d6efd'
        });
        return; 
    }

    const fabricSelect = document.getElementById('fabricSelect');
    const qtyInput = document.getElementById('qtyInput');
    const unitSelect = document.getElementById('unitSelect');
    
    if (fabricSelect.value === "") {
        Swal.fire({
            icon: 'error',
            title: 'ลืมเลือกบริการ!',
            text: 'กรุณาเลือกบริการและชนิดผ้าก่อนครับ',
            confirmButtonColor: '#dc3545'
        });
        return;
    }

    const option = fabricSelect.options[fabricSelect.selectedIndex];
    
    cartArray.push({
        service_id: fabricSelect.value,
        name: option.getAttribute('data-name'),
        qty: parseFloat(qtyInput.value),
        unit: option.getAttribute('data-unit') || "ชิ้น",
        price: parseFloat(option.getAttribute('data-price'))
    });

    qtyInput.value = "1";
    fabricSelect.value = "";
    document.getElementById('priceDisplay').value = "0.00";

    renderCart();
}

function removeItem(index) {
    cartArray.splice(index, 1); 
    renderCart(); 
}

function renderCart() {
    const tbody = document.getElementById('cartBody');
    tbody.innerHTML = ''; 
    total = 0; 

    if (cartArray.length === 0) {
        tbody.innerHTML = `
            <tr id="emptyCartRow">
                <td colspan="5" class="text-center py-4 text-muted">ยังไม่มีรายการซักรีด</td>
            </tr>
        `;
        document.getElementById('totalPrice').innerText = "0.00";
        document.getElementById('cartData').value = "[]";
        return;
    }

    cartArray.forEach((item, index) => {
        const subtotal = item.price * item.qty;
        total += subtotal;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="text-dark fw-medium">${item.name}</td>
            <td class="text-center text-muted">${item.price.toFixed(2)} ฿ / ${item.unit}</td>
            <td class="text-center fw-medium text-dark">${item.qty} ${item.unit}</td>
            <td class="text-end text-dark fw-bold pe-3">${subtotal.toFixed(2)}</td>
            <td class="text-center">
                <button type="button" class="btn btn-sm text-danger bg-danger bg-opacity-10 border-0 rounded-2 shadow-sm d-inline-flex align-items-center justify-content-center" 
                    onclick="removeItem(${index})" title="ลบรายการนี้" style="width: 32px; height: 32px; padding: 0;">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById('totalPrice').innerText = total.toFixed(2);
    document.getElementById('cartData').value = JSON.stringify(cartArray);
}