document.addEventListener("DOMContentLoaded", function() {
    const filterBill = document.getElementById('filterBill');
    const filterCustomer = document.getElementById('filterCustomer');
    const filterEmp = document.getElementById('filterEmp');
    const filterService = document.getElementById('filterService');
    const filterStatus = document.getElementById('filterStatus');
    const pageSizeSelect = document.getElementById('pageSize');
    const searchBtn = document.getElementById('searchBtn');
    const noMatchRow = document.getElementById('noMatchRow');
    const paginationControls = document.getElementById('paginationControls');
    
    const allRows = Array.from(document.querySelectorAll('#queueTableBody tr.order-group'));
    
    function initDropdowns() {
        const emps = [...new Set(allRows.map(r => r.getAttribute('data-emp')))]
                        .filter(x => x && x.trim() !== "").sort();
        
        filterEmp.innerHTML = '<option value="">ทั้งหมด</option>'; 
        emps.forEach(e => {
            let opt = document.createElement('option');
            opt.value = e;
            opt.textContent = e;
            filterEmp.appendChild(opt);
        });

        const services = [...new Set(allRows.map(r => r.getAttribute('data-service')))]
                            .filter(x => x && x.trim() !== "").sort();
        
        filterService.innerHTML = '<option value="">ทั้งหมด</option>'; 
        services.forEach(s => {
            let opt = document.createElement('option');
            opt.value = s;
            opt.textContent = s;
            filterService.appendChild(opt);
        });

        filterStatus.innerHTML = `
            <option value="">ทั้งหมด</option>
            <option value="รอดำเนินการ">รอดำเนินการ</option>
            <option value="กำลังดำเนินการ">กำลังดำเนินการ</option>
            <option value="งานเสร็จสิ้น">งานเสร็จสิ้น</option>
        `;
    }

    let currentPage = 1;

    function renderTable() {
        const billVal = filterBill.value.toLowerCase();
        const cusVal = filterCustomer.value.toLowerCase();
        const empVal = filterEmp.value;
        const srvVal = filterService.value;
        const statVal = filterStatus.value;
        const pageSize = parseInt(pageSizeSelect.value);

        const uniqueOrderIDs = [...new Set(allRows.map(r => r.getAttribute('data-order-id')))];
        
        const filteredOrderIDs = uniqueOrderIDs.filter(id => {
            const billRows = allRows.filter(r => r.getAttribute('data-order-id') === id);
            const firstRow = billRows[0];

            const matchBill = firstRow.getAttribute('data-bill').toLowerCase().includes(billVal);
            const matchCus = firstRow.getAttribute('data-cus').toLowerCase().includes(cusVal);
            const matchEmp = empVal === "" || firstRow.getAttribute('data-emp') === empVal;
            const matchService = srvVal === "" || billRows.some(r => r.getAttribute('data-service') === srvVal);
            const matchStatus = statVal === "" || billRows.some(r => {
                const s = r.getAttribute('data-status');
                if (statVal === 'รอดำเนินการ') return s.includes('รอดำเนินการ') || s.includes('รอชำระเงิน');
                if (statVal === 'งานเสร็จสิ้น') return s.includes('เสร็จสิ้น');
                return s.includes(statVal);
            });

            return matchBill && matchCus && matchEmp && matchService && matchStatus;
        });

        const totalBills = filteredOrderIDs.length;
        const totalPages = Math.ceil(totalBills / pageSize) || 1;
        if (currentPage > totalPages) currentPage = totalPages;

        const startIndex = (currentPage - 1) * pageSize;
        const endIndex = startIndex + pageSize;
        const visibleOrderIDs = filteredOrderIDs.slice(startIndex, endIndex);

        allRows.forEach(row => {
            row.style.display = visibleOrderIDs.includes(row.getAttribute('data-order-id')) ? '' : 'none';
        });

        noMatchRow.style.display = (totalBills === 0 && allRows.length > 0) ? '' : 'none';
        
        const startDisp = totalBills > 0 ? startIndex + 1 : 0;
        const endDisp = Math.min(endIndex, totalBills);
        document.getElementById('pageInfo').textContent = `แสดงบิลที่ ${startDisp} ถึง ${endDisp} จากทั้งหมด ${totalBills} บิล`;
        
        renderPagination(totalPages);
    }

    function renderPagination(totalPages) {
        paginationControls.innerHTML = '';
        
        const createBtn = (label, target, active=false, disabled=false) => {
            const li = document.createElement('li');
            li.className = `page-item ${active?'active':''} ${disabled?'disabled':''}`;
            const a = document.createElement('a');
            a.className = 'page-link shadow-none';
            a.href = 'javascript:void(0);';
            a.textContent = label;
            if(!disabled) {
                a.onclick = () => { currentPage = target; renderTable(); };
            }
            li.appendChild(a);
            return li;
        };

        paginationControls.appendChild(createBtn('ก่อนหน้า', currentPage - 1, false, currentPage === 1));
        for(let i=1; i<=totalPages; i++) {
            paginationControls.appendChild(createBtn(i, i, currentPage === i));
        }
        paginationControls.appendChild(createBtn('ถัดไป', currentPage + 1, false, currentPage === totalPages || totalPages === 0));
    }

    initDropdowns();
    
    searchBtn.addEventListener('click', () => { 
        currentPage = 1; 
        renderTable(); 
    });

    pageSizeSelect.addEventListener('change', () => { 
        currentPage = 1; 
        renderTable(); 
    });

    renderTable();
});