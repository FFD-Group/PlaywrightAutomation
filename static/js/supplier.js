document.addEventListener('alpine:init', () => {

    Alpine.data('currentSupplier', () => ({
        automations: [],
        supplier_id: null,
        selected_automation_id: null,

        displaySupplierData(event) {
            // Load supplier data from event
            console.log("Supplier data loading...");
            console.log(event.detail);
            this.automations = event.detail.automations;
            this.supplier_id = event.detail.supplier_id;
        },

        deleteSelectedAutomation() {
            if (!confirm("Are you sure you want to delete automation with the ID: " + this.selected_automation_id)) {
                return;
            }
            fetch("/automation/" + this.supplier_id + "/" + this.selected_automation_id + "/delete", {
                method: 'DELETE'
            })
            .then((response) => {
                if (!response.ok) {
                    throw "Error deleting automation!";
                }
            })
            .finally(() => {
                window.dispatchEvent(new CustomEvent("fetchsupplier"));
            })
            .catch((error) => {
                console.error(error);
            })
        },

        editSelectedAutomation() {
            let edit_url = new URL("/automation/" + this.supplier_id + "/" + this.selected_automation_id + "/edit", document.baseURI).href;
            window.location.href = edit_url;
        }
    }));

    Alpine.data('supplierSelection', () => ({
        selection: null,
        load_disabled: true,

        fetchSupplierData() {
            // Fetch supplier data and dispatch event 'supplierloaded'
            fetch("/automations/" + this.selection, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            })
            .then((response) => {
                if (!response.ok) {
                    throw "Supplier data not fetched.";
                }
                return response.json();
            })
            .then((supplier_data) => {
                window.dispatchEvent(new CustomEvent("supplierloaded", {
                    detail: {
                        automations: supplier_data,
                        supplier_id: this.selection
                    }
                }));
            })
            .catch((error) => {
                console.log(error);
            });
        }
    }));

});