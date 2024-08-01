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
            if (!this.selected_automation_id) {
                alert("Please select an automation to delete.");
                return;
            }
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

        // editSelectedAutomation() {
        //     let edit_url = new URL("/automation/" + this.supplier_id + "/" + this.selected_automation_id + "/edit", document.baseURI).href;
        //     window.location.href = edit_url;
        // }
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
                let select = document.querySelector("#supplierselect");
                let label = select.selectedOptions[0].text;
                Alpine.store("selectedSupplierLabel", label);
                Alpine.store("supplierId", this.selection);
            })
            .catch((error) => {
                console.log(error);
            });
        }
    }));

    Alpine.data('newAutomation', () => ({
        type: null,
        url: '',
        name: '',
        location: '',
        supplier_id: null,

        save() {
            if (!Alpine.store('supplierId')) {
                alert("Please select and load a supplier first.");
                return;
            }
            if (this.type == 0) { // automation type
                // send user to builder with data
                let url = new URL("/automations/" + this.supplier_id + "/new?name=" + encodeURIComponent(this.name) + "&save_location=" + encodeURIComponent(this.location));
                window.location.href = url;
            } 
            // download type                
            data = {
                supplier_id: Alpine.store('supplierId'),
                automation_name: this.name,
                save_location: this.location,
                download_url: this.url
            };
            fetch("/automations/download/save", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then((response) => {
                if (!response.ok) {
                    throw "Failed to save download!";
                }
                return response.json()
            })
            .then((inserted_row) => {
                alert("Inserted row with ID: " + inserted_row);
            })
            .finally(() => {
                // Reload the existing automation list
                window.dispatchEvent(new CustomEvent("fetchsupplier"));
            })
            .catch((error) => {
                console.error(error);
            });
        }
    }));

});