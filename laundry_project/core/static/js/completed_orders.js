function showItemsModal(billId, itemsStr, qty, unit, price) {
    document.getElementById('modalBillId').innerText = billId;
    document.getElementById('modalTotalQty').innerText = qty;
    document.getElementById('modalUnit').innerText = unit;
    document.getElementById('modalTotalPrice').innerText = price;
    
    const itemListContainer = document.getElementById('modalItemList');
    const itemArray = itemsStr.split('|').map(i => i.trim()).filter(i => i !== "");
    let htmlContent = '<div class="list-group list-group-flush border rounded-3 overflow-hidden">';
    
    itemArray.forEach(itemData => {
        const parts = itemData.split(':');
        const itemName = parts[0] || '-';
        const itemQty = parts[1] || '0';
        const itemPrice = parseFloat(parts[2] || '0').toFixed(2);
        
        htmlContent += `
            <div class="list-group-item d-flex justify-content-between align-items-center py-2 bg-white">
                <span class="text-secondary small"><i class="fa-solid fa-check text-success me-2"></i>${itemName}</span>
                <div>
                    <span class="badge bg-light text-primary border border-primary-subtle fw-bold me-2">x ${itemQty}</span>
                    <span class="text-dark fw-bold small">฿${(parseInt(itemQty) * itemPrice).toFixed(2)}</span>
                </div>
            </div>`;
    });
    htmlContent += '</div>';
    itemListContainer.innerHTML = htmlContent;
    new bootstrap.Modal(document.getElementById('itemsModal')).show();
}

document.addEventListener("DOMContentLoaded", function() {
    const fBill = document.getElementById('filterBill');
    const fCus = document.getElementById('filterCustomer');
    const fStart = document.getElementById('filterStartDate');
    const fEnd = document.getElementById('filterEndDate');
    const pSize = document.getElementById('pageSize');
    const searchBtn = document.getElementById('searchBtn'); 
    const pgControls = document.getElementById('paginationControls');
    const noMatch = document.getElementById('noMatchRow');
    const allRows = Array.from(document.querySelectorAll('#historyTableBody tr.order-row'));
    let currentPage = 1;

    function renderTable() {
        const billV = fBill.value.toLowerCase();
        const cusV = fCus.value.toLowerCase();
        const startV = fStart.value;
        const endV = fEnd.value;
        const size = parseInt(pSize.value);

        const filteredRows = allRows.filter(row => {
            const billText = row.querySelector('.col-bill').textContent.toLowerCase();
            const cusName = row.querySelector('.cus-name').textContent.toLowerCase();
            const rowStart = row.getAttribute('data-start-date');
            const rowEnd = row.getAttribute('data-end-date');
            return billText.includes(billV) && cusName.includes(cusV) && 
                   (startV === "" || rowStart === startV) && (endV === "" || rowEnd === endV);
        });

        const total = filteredRows.length;
        const totalP = Math.ceil(total / size) || 1;
        if (currentPage > totalP) currentPage = totalP;
        const startIdx = (currentPage - 1) * size;
        const endIdx = startIdx + size;

        allRows.forEach(row => row.style.display = 'none');
        filteredRows.slice(startIdx, endIdx).forEach(row => row.style.display = '');

        noMatch.style.display = (total === 0 && allRows.length > 0) ? '' : 'none';
        
        const startDisp = total > 0 ? startIdx + 1 : 0;
        document.getElementById('pageInfo').textContent = `แสดงที่ ${startDisp} ถึง ${Math.min(endIdx, total)} จากทั้งหมด ${total} รายการ`;
        renderPagination(totalP);
    }

    function renderPagination(totalP) {
        pgControls.innerHTML = '';
        const createBtn = (label, target, active = false, disabled = false) => {
            const li = document.createElement('li');
            li.className = `page-item ${active ? 'active' : ''} ${disabled ? 'disabled' : ''}`;
            const a = document.createElement('a');
            a.className = 'page-link shadow-none';
            a.href = 'javascript:void(0);';
            a.textContent = label;
            if (!disabled) {
                a.onclick = () => { currentPage = target; renderTable(); window.scrollTo({top: 0, behavior: 'smooth'}); };
            }
            li.appendChild(a);
            return li;
        };

        pgControls.appendChild(createBtn('ก่อนหน้า', currentPage - 1, false, currentPage === 1));
        for (let i = 1; i <= totalP; i++) {
            pgControls.appendChild(createBtn(i, i, currentPage === i));
        }
        pgControls.appendChild(createBtn('ถัดไป', currentPage + 1, false, currentPage === totalP || totalP === 0));
    }

    searchBtn.addEventListener('click', () => { currentPage = 1; renderTable(); });
    pSize.addEventListener('change', () => { currentPage = 1; renderTable(); });
    renderTable();
});

async function exportToExcel() {
    const fBill = document.getElementById('filterBill').value.toLowerCase();
    const fCus = document.getElementById('filterCustomer').value.toLowerCase();
    const fStart = document.getElementById('filterStartDate').value;
    const fEnd = document.getElementById('filterEndDate').value;
    
    const allRows = Array.from(document.querySelectorAll('#historyTableBody tr.order-row'));
    
    const exportRows = allRows.filter(row => {
        const billText = row.querySelector('.col-bill').textContent.toLowerCase();
        const cusName = row.querySelector('.cus-name').textContent.toLowerCase();
        const rowStart = row.getAttribute('data-start-date');
        const rowEnd = row.getAttribute('data-end-date');
        return billText.includes(fBill) && cusName.includes(fCus) && 
               (fStart === "" || rowStart === fStart) && (fEnd === "" || rowEnd === fEnd);
    });

    if (exportRows.length === 0) {
        Swal.fire({ icon: 'warning', title: 'ไม่มีข้อมูล', text: 'ไม่พบข้อมูลสำหรับการ Export', confirmButtonColor: '#0d6efd' });
        return;
    }

    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('รายงานประวัติงานที่เสร็จสิ้น');

    worksheet.columns = [
        { key: 'billId', width: 15 },
        { key: 'date', width: 20 },
        { key: 'completedDate', width: 20 }, 
        { key: 'customer', width: 25 },
        { key: 'item', width: 60 },
        { key: 'qty', width: 15 },
        { key: 'price', width: 20 }
    ];

    worksheet.mergeCells('A1:G1');
    const titleRow = worksheet.getRow(1);
    titleRow.getCell(1).value = 'ประวัติงานที่เสร็จสิ้น (พร้อมรายได้สุทธิ)';
    titleRow.getCell(1).font = { size: 16, bold: true };
    titleRow.getCell(1).alignment = { horizontal: 'center', vertical: 'middle' };

    worksheet.mergeCells('A2:G2');
    const subtitleRow = worksheet.getRow(2);
    const now = new Date();
    const formattedDate = now.toLocaleDateString('th-TH') + ' เวลา ' + now.toLocaleTimeString('th-TH');
    subtitleRow.getCell(1).value = `Export ณ วันที่: ${formattedDate}`;
    subtitleRow.getCell(1).font = { size: 14 };
    subtitleRow.getCell(1).alignment = { horizontal: 'center', vertical: 'middle' };

    const headerRow = worksheet.getRow(3);
    headerRow.values = ['รหัสบิล', 'วันที่รับออเดอร์', 'วันที่สิ้นสุด', 'ชื่อลูกค้า', 'รายการผ้า', 'จำนวน/ตัว', 'รวมสุทธิ'];
    for (let i = 1; i <= 7; i++) {
        let cell = headerRow.getCell(i);
        cell.font = { size: 14, bold: true, color: { argb: 'FFFFFFFF' } }; 
        cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF0D6EFD' } }; 
        cell.alignment = { vertical: 'middle', horizontal: 'center' };
        cell.border = { top: { style: 'thin' }, left: { style: 'thin' }, bottom: { style: 'thin' }, right: { style: 'thin' } };
    }

    let grandTotal = 0;

    exportRows.forEach((row, index) => {
        const billId = row.querySelector('.col-bill').textContent.trim();
        const orderDate = row.querySelector('td:nth-child(2)').textContent.trim().split(' ')[0]; 
        const completedDate = row.querySelector('td:nth-child(6)').textContent.trim().split(' ')[0]; 
        const cusName = row.querySelector('.cus-name').textContent.trim();
        
        const itemsStr = row.getAttribute('data-items') || '';
        const totalQty = parseInt(row.getAttribute('data-qty') || '0');
        const price = parseFloat(row.getAttribute('data-price') || '0.00');

        grandTotal += price;

        // แยกข้อมูลด้วยเครื่องหมาย |
        const itemArray = itemsStr.split('|').map(i => i.trim()).filter(i => i !== "");
        const bgColor = (index % 2 === 0) ? 'FFF8F9FA' : 'FFFFFFFF'; 

        if (itemArray.length === 0) {
            let newRow = worksheet.addRow({ billId, date: orderDate, completedDate, customer: cusName, item: '-', qty: totalQty, price });
            styleDataRow(newRow, bgColor);
        } else {
            let startRow = worksheet.rowCount + 1; // จดแถวเริ่มต้นไว้รอ Merge

            itemArray.forEach((itemData, i) => {
                const parts = itemData.split(':');
                const itemName = parts[0] ? parts[0].trim() : '-';
                const itemQty = parts[1] ? parseInt(parts[1].trim()) : 0;
                const unitPrice = parts[2] ? parseFloat(parts[2].trim()) : 0;
                
                // คำนวณราคาของรายการนั้น: จำนวน x ราคาต่อหน่วย
                const itemLineTotal = (itemQty * unitPrice).toFixed(2);
                const formattedText = `${itemName} x${itemQty} รวม ${itemLineTotal}`;

                let newRow = worksheet.addRow({ 
                    billId: i === 0 ? billId : '', 
                    date: i === 0 ? orderDate : '', 
                    completedDate: i === 0 ? completedDate : '', 
                    customer: i === 0 ? cusName : '', 
                    item: formattedText, 
                    qty: i === 0 ? totalQty : '', 
                    price: i === 0 ? price : '' 
                });
                styleDataRow(newRow, bgColor);
            });

            // ผสานเซลล์รหัสบิล, วันที่, ลูกค้า, จำนวนรวม, และราคารวม ถ้ารายการผ้ามีมากกว่า 1 บรรทัด
            if (itemArray.length > 1) {
                let endRow = worksheet.rowCount;
                ['A', 'B', 'C', 'D', 'F', 'G'].forEach(col => {
                    worksheet.mergeCells(`${col}${startRow}:${col}${endRow}`);
                });
            }
        }
    });

    let totalRow = worksheet.addRow({ billId: '', date: '', completedDate: '', customer: '', item: '', qty: 'รวมสุทธิทั้งหมด', price: grandTotal });
    for (let i = 1; i <= 7; i++) {
        let cell = totalRow.getCell(i);
        cell.font = { size: 14, bold: true, color: { argb: 'FF000000' } };
        cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFC107' } }; 
        cell.border = { top: { style: 'thin' }, left: { style: 'thin' }, bottom: { style: 'thin' }, right: { style: 'thin' } };
    }
    worksheet.mergeCells(`A${worksheet.rowCount}:E${worksheet.rowCount}`);
    totalRow.getCell(6).alignment = { horizontal: 'right', vertical: 'middle' };
    totalRow.getCell(7).numFmt = '#,##0.00';
    totalRow.getCell(7).alignment = { horizontal: 'right', vertical: 'middle' };

    const buffer = await workbook.xlsx.writeBuffer();
    const dateStr = new Date().toISOString().slice(0,10);
    saveAs(new Blob([buffer]), `ประวัติงานที่เสร็จสิ้น_${dateStr}.xlsx`);
}

function styleDataRow(row, bgColor) {
    for (let i = 1; i <= 7; i++) {
        let cell = row.getCell(i);
        cell.font = { size: 14 }; 
        cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: bgColor } };
        // ตั้งให้อยู่ตรงกลาง เพื่อให้เวลา Merge Cell แล้วข้อความอยู่กึ่งกลางสวยๆ
        cell.alignment = { vertical: 'middle', horizontal: 'center' };
        cell.border = { top: { style: 'thin' }, left: { style: 'thin' }, bottom: { style: 'thin' }, right: { style: 'thin' } };
    }
    row.getCell(4).alignment = { vertical: 'middle', horizontal: 'left' }; // ลูกค้าชิดซ้าย
    row.getCell(5).alignment = { vertical: 'middle', horizontal: 'left' }; // รายการผ้าชิดซ้าย
    
    const priceCell = row.getCell(7);
    if(priceCell.value !== '') {
        priceCell.numFmt = '#,##0.00';
        priceCell.alignment = { vertical: 'middle', horizontal: 'right' }; // ราคาชิดขวา
    }
}
