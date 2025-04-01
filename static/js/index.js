document.addEventListener('alpine:init', () => {

    Alpine.store("supplierUploads", undefined);

    Alpine.data('FlashMessages', () => ({
        flashed_messages: [],

        addFlashMessage(detail) {
            if (detail) {
                this.flashed_messages.push(detail);
                idx = this.flashed_messages.indexOf(detail);
                setTimeout(() => {
                    if (idx > -1) {
                        this.flashed_messages.splice(idx, 1);
                    }
                }, 5000);
            }
        }
    }));

    Alpine.data('currentSupplier', () => ({
        automations: [],
        supplier_id: null,
        selected_automation_id: null,

        displaySupplierData(event) {
            // Load supplier data from event
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
        }
    }));

    Alpine.data('uploadHistory', () => ({
        historyAvailable: false,
        showHistory: false,
        uploads: [],

        setHistoryAvailable(b) {
            this.showHistory = false;
            this.historyAvailable = b;
        },

        getFormattedDateTime(timestamp) {
            date = new Date(timestamp * 1000); // multiple by 1000 because of difference between JS and Python timestamps
            return date.toLocaleDateString('en-GB', {
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        fetchUploads() {
            supplierId = Alpine.store('supplierId');
            if (!supplierId) {
                throw "No supplier ID";
            }
            // Fetch supplier uploads
            fetch("/uploads/" + supplierId, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            })
            .then((response) => {
                if (!response.ok) {
                    throw "Supplier uploads not fetched.";
                }
                return response.json();
            })
            .then((supplier_uploads) => {
                this.uploads = supplier_uploads;
                this.showHistory = true;
            })
            .catch((error) => {
                console.error(error);
                this.showHistory = false;
            });
        }
    }));

    Alpine.data('supplierSelection', () => ({
        selection: null,
        load_disabled: true,

        checkPassedSupplier() {
            const queryString = window.location.search;
            const urlParams = new URLSearchParams(queryString);
            passed_supplier = urlParams.get("supplier_id");
            if (passed_supplier) {
                this.selection = passed_supplier;
                this.fetchSupplierData();
            }
        },

        fetchSupplierData() {
            // Fetch supplier automations
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
                supplier_data.forEach((automation) => {
                    if (automation["processing_options"]) {
                        automation["processing_options"] = JSON.parse(automation["processing_options"]["options"].replace(/'/g, '"'));
                    }
                });
                window.dispatchEvent(new CustomEvent("supplierloaded", {
                    detail: {
                        automations: supplier_data,
                        supplier_id: this.selection
                    }
                }));
                window.dispatchEvent(new CustomEvent("uploadsavailable"));
                let select = document.querySelector("#supplierselect");
                let label = select.selectedOptions[0].text;
                Alpine.store("selectedSupplierLabel", label);
                Alpine.store("supplierId", this.selection);
                document.getElementById("upload_supplier_id").value = this.selection;
                document.getElementById("upload_supplier_name").value = label;
            })
            .catch((error) => {
                console.error(error);
            });
        }
    }));

    Alpine.data('newAutomation', () => ({
        type: null,
        url: '',
        name: '',
        location: '',
        disable_save: true,
        supplier_id: null,
        show_sample_upload: true,
        show_column_mappings: false,
        show_processing_options: false,
        sample_file_columns: [],
        sample_file: null,
        skip_rows: 0,
        cm_sku: "",
        cm_stock_availability: "",
        cm_price: "",
        cm_cost: "",
        cm_stock_quantity: "",
        specials_strategy_description: "some text",
        processing_file_type: "Stock & Price file",
        stock_strategy: null,
        price_strategy: "list_prices_only",
        disable_price_strategy: false,
        pricing_markup: 0.00,
        pricing_discount: 0.00,
        specials_type: "seperate_specials_file",
        adv_pricing_group_column: "",
        adv_pricing_group_starts_with: false,
        show_adv_pricing: false,
        adv_pricing_groups: [],

        backToColumnMappings() {
            this.show_processing_options = false;
            this.show_column_mappings = true;
            this.disable_save = true;
        },

        pricingGroupByChange() {
            if (!this.sample_file) {
                console.error("No sample file provided!");
                return;
            }
            const data = new FormData();
            const files = document.getElementById("sample_upload_file");
            data.append("file", files.files[0]);
            data.append("skip_rows", document.getElementById("sample_skip_rows").value);
            data.append("group_by_column", this.adv_pricing_group_column);
            fetch("/distinct-column-values", {
                method: 'POST',
                body: data
            })
            .then((response) => {
                return response.json();
            })
            .then((result) => {
                if (result["result"] == "error") {
                    throw Error("An error occured!" + result["detail"]);
                }
                console.log(result);
                groups = result["detail"];
                this.adv_pricing_groups = [];
                groups.forEach((group) => {
                    if (!group) return;
                    this.adv_pricing_groups.push({
                        value: group,
                        discount: undefined,
                        markup: undefined,
                        extra: undefined
                    });
                });
                window.dispatchEvent(new CustomEvent("newflashmessage", {detail: {"category": "success", "message": "Column values read, enter pricing data."}}));
            })
            .catch((error) => {
                window.dispatchEvent(new CustomEvent("newflashmessage", {detail: {"category": "error", "message": error}}));
            });
        },

        addGrouping() {
            this.adv_pricing_groups.push({
                value: "",
                discount: undefined,
                markup: undefined
            });
        },

        deleteGroup(group) {
            this.adv_pricing_groups.forEach((existingGroup) => {
                if (existingGroup["value"] == group["value"]
                    && existingGroup["discount"] == group["discount"]
                    && existingGroup["markup"] == group["markup"]
                ) {
                    this.adv_pricing_groups.splice(this.adv_pricing_groups.indexOf(existingGroup), 1);
                    return;
                }
            })
        },

        setColumnMapping() {
            if (this.cm_sku == "") {
                window.dispatchEvent(new CustomEvent("newflashmessage", {detail:{"category": "error", "message": "SKU is a required column."}}));
                return;
            }
            // work out file type depending on mapped columns
            if ((this.cm_price == "" && this.cm_cost == "")
                && (this.cm_stock_availability != "" || this.cm_stock_quantity != ""))
            {
                this.processing_file_type = "Stock file";
                this.disable_price_strategy = true;
                this.price_strategy = "";
            } 
            else if ((this.cm_stock_availability == "" && this.cm_stock_quantity == "")
                    && (this.cm_price != "" || this.cm_cost != ""))
            {
                this.processing_file_type = "Price file";
                this.disable_price_strategy = false;
            }
            else this.processing_file_type = "Stock & Price file";
            // work out stock strategy depending on mapped columns
            if (this.processing_file_type != "Price file") {
                if (this.cm_stock_availability == "" && this.cm_stock_quantity != "") this.stock_strategy = "Levels Only";
                else if (this.cm_stock_availability != "" && this.cm_stock_quantity == "") this.stock_strategy = "Availability Only";
                else this.stock_strategy = "Availability & Levels";
            } else this.stock_strategy = "No Stock Data";
            // hide column mappings and show processing options
            this.show_column_mappings = false;
            this.show_processing_options = true;
            this.disable_save = false;
        },

        updateColumnMappings(target) {
            if (target.value == "") return;
            ["cm_sku", "cm_stock_availability", "cm_price", "cm_cost", "cm_stock_quantity"].forEach((select) => {
                if (target.name == select) return;
                if (this[select] == target.value) {
                    window.dispatchEvent(new CustomEvent("newflashmessage", {detail:{"category": "error", "message": "Can't duplicate column mappings."}}));
                    target._x_model.set("");
                    return;
                }
            });
        },

        uploadSampleFile() {
            if (!this.sample_file) {
                console.error("No sample file provided!");
                return;
            }
            const data = new FormData();
            const files = document.getElementById("sample_upload_file");
            data.append("file", files.files[0]);
            data.append("skip_rows", document.getElementById("sample_skip_rows").value);
            fetch("/upload-sample-file", {
                method: 'POST',
                body: data
            })
            .then((response) => {
                return response.json();
            })
            .then((result) => {
                if (result["result"] == "error") {
                    throw Error("An error occured!" + result["detail"]);
                }
                this.sample_file_columns = result["detail"];
                console.log(this.sample_file_columns);
                window.dispatchEvent(new CustomEvent("newflashmessage", {detail: {"category": "success", "message": "Sample file read. Map your columns."}}));
                this.show_sample_upload = false;
                this.show_column_mappings = true;
            })
            .catch((error) => {
                window.dispatchEvent(new CustomEvent("newflashmessage", {detail: {"category": "error", "message": error}}));
            });
        },

        save() {
            this.supplier_id = Alpine.store('supplierId');
            if (!this.supplier_id) {
                alert("Please select and load a supplier first.");
                return;
            }
            
            processing_options = {
                "skip_rows": this.skip_rows,
                "sku_column": this.cm_sku,
                "stock_availability_column": this.cm_stock_availability,
                "price_column": this.cm_price,
                "cost_column": this.cm_cost,
                "stock_quantity_column": this.cm_stock_quantity,
                "data_type": this.processing_file_type,
                "stock_strategy": this.stock_strategy,
                "price_strategy": this.price_strategy,
                "pricing_markup": this.pricing_markup,
                "pricing_discount": this.pricing_discount,
                "specials_type": this.specials_type,
                "adv_pricing_group_column": this.adv_pricing_group_column,
                "adv_pricing_group_starts_with": this.adv_pricing_group_starts_with,
                "adv_pricing_groups": this.adv_pricing_groups
            };
            if (this.type == 0) { // automation type
                fetch("/automations/validate_processing_options", {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(processing_options)
                })
                .then((response) => {
                    if (!response.ok) {
                        throw "Error saving processing options.";
                    }
                    return response.json();
                })
                .then((validation) => {
                    if (validation["result"] == "error") {
                        window.dispatchEvent(new CustomEvent("newflashmessage", {detail:{"category": "error", "message": validation["detail"]}}));
                        console.error(validation);
                        throw "Validation failed.";
                    }
                    console.log(validation);
                })
                .then(() => {
                    supplier_name = Alpine.store('selectedSupplierLabel');
                    let url = new URL("/automation-builder/" + this.supplier_id + "/new?name=" + encodeURIComponent(this.name) + "&save_location=" + encodeURIComponent(this.location) + "&supplier_name=" + encodeURIComponent(supplier_name), document.baseURI);
                    localStorage.setItem("processing_options", JSON.stringify(processing_options));
                    window.location.href = url;
                    return;
                })
                .catch((error) => {
                    console.error(error);
                });
            }   
            // download type                
            data = {
                supplier_id: Alpine.store('supplierId'),
                automation_name: this.name,
                save_location: this.location,
                download_url: this.url,
                supplier_name: Alpine.store('selectedSupplierLabel')
            };
            fetch("/automations/validate_processing_options", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(processing_options)
            })
            .then((response) => {
                if (!response.ok) {
                    throw "Error saving processing options.";
                }
                return response.json();
            })
            .then((validation) => {
                if (validation["result"] == "error") {
                    window.dispatchEvent(new CustomEvent("newflashmessage", {detail:{"category": "error", "message": validation["detail"]}}));
                    console.error(validation);
                    throw "Validation failed.";
                }
                console.log(validation);
            })
            .then(() => {
                return fetch("/automations/download/save", {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
            })
            .then((response) => {
                if (!response.ok) {
                    throw "Failed to save download!";
                }
                return response.json()
            })
            .then((inserted_row) => {
                alert("Inserted download with ID: " + inserted_row);
                // Saving processing options linked with ID:
                return fetch("/automations/" + inserted_row + "/save_processing_options", {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(processing_options)
                });
            })
            .then((save_processing_options_response) => {
                console.log(save_processing_options_response);
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

    Alpine.data('existingAutomation', () => ({
        collapsed: true,
        schedule,
        customtime: null,
        error: null,

        get_automation_status_colour(last_run_result, next_run_time, schedule) {
            if (!schedule) { // Unscheduled
                return 'bg-slate-300';
            }
            if (schedule && !next_run_time) { // Paused
                return 'bg-amber-400';
            }
            if (last_run_result) {
                successful = last_run_result.includes('Success'); // Running
                if (successful) return 'bg-green-600';
                return 'bg-red-600';
            }
            return 'bg-slate-300'; // Default
        },

        get_formatted_run_time(next_run_time) {
            if (next_run_time) {
                result = new Date(next_run_time);
                formatted = result.toLocaleString('en-GB', {
                    'hour12': true,
                    'weekday': 'short',
                    'month': 'short',
                    'day': 'numeric',
                    'dayPeriod': 'narrow',
                    'hour': 'numeric',
                    'minute': '2-digit'
                });
                return formatted;
            }
            return 'Unscheduled';
        },

        pause_automation(automation_id) {
            if (!confirm("Really pause the schedule for job with ID: " + automation_id + "?")) {
                return;
            }
            fetch("/scheduler/jobs/" + automation_id + "/pause", {
                method: 'POST'
            })
            .then((response) => {
                if (!response.ok) {
                    console.log("error");
                }
                return response.json();
            })
            .then((job) => {
                alert("Job Paused. It will not run again until resumed.");
                // Reload the existing automation list
                window.dispatchEvent(new CustomEvent("fetchsupplier"));
            })
            .catch((error) => {
                console.error(error);
            })
        },

        resume_automation(automation_id) {
            if (!confirm("Really resume the schedule for job with ID: " + automation_id + "?")) {
                return;
            }
            fetch("/scheduler/jobs/" + automation_id + "/resume", {
                method: 'POST'
            })
            .then((response) => {
                if (!response.ok) {
                    console.log("error");
                }
                return response.json();
            })
            .then((job) => {
                alert("Job Resumed. It will run on it's schedule until paused or deleted.");
                // Reload the existing automation list
                window.dispatchEvent(new CustomEvent("fetchsupplier"));
            })
            .catch((error) => {
                console.error(error);
            })
        },

        schedule_automation(event, automation_id, automation_type) {
            event.preventDefault();
            if (!this.schedule || (this.schedule == 'custom' && !this.customtime)) {
                this.error = 'Invalid entry.';
                return;
            }
            this.error = null;

            if (this.schedule != 'custom') {
                this.customtime = null;
            }

            // fetch to endpoint to set automation schedule
            data = {
                schedule: this.schedule,
                time: this.customtime,
                type: automation_type
            };

            fetch("/schedule/" + automation_id, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then((response) => {
                if (!response.ok) {
                    console.error(response.error);
                }
                return response.json();
            })
            .then((next_run_time) => {
                let next_run_datetime = new Date(next_run_time);
                alert("Schedule has been changed to " + this.schedule + ", next run time will be: " + next_run_datetime.toLocaleString());
                window.dispatchEvent(new CustomEvent("fetchsupplier"));
            })
            .catch((error) => {
                console.error(error);
            });
        }
    }));

});