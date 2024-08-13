document.addEventListener('alpine:init', () => {

    Alpine.data('automationInfo', () => ({
        name: '',
        save_location: '',

        loadParameters() {
            const queryString = window.location.search;
            const urlParams = new URLSearchParams(queryString);
            this.name = urlParams.get("name");
            this.save_location = urlParams.get("save_location");
        }
    }));

    Alpine.data('action', () => ({
        form_els: [],
        action: '',
        pw_method: '',
        pw_method_arg: '',
        pw_method_arg_2: '',
        valid: true,
        errors: [],

        constructor(htmlAction) {
            if (htmlAction) {
                this.populateFormElements(htmlAction);
                htmlAction.removeAttribute("draggable");
                classes = htmlAction.classList;
                console.log(classes);
                classes.remove("action");
                this.action = classes[0];
                console.log(this.action);
            }
        },

        deleteAction(el) {
            let target = document.getElementById("target");
            target.removeChild(el.parentNode);
        },

        populateFormElements(el) {
            el.querySelectorAll("select,input").forEach((htmlFormEl) => {
                let required = htmlFormEl.hasAttribute("required");
                let type = htmlFormEl.tagName;
                let value = (htmlFormEl).value;
                let validation = htmlFormEl.getAttribute("pattern") || undefined;
                let fe = new FormElement(required, type, value, validation);
                this.form_els.push(fe);
            });
        },

        dragStartHandler(ev) {
            if (ev.target instanceof Element && ev.target.classList.contains("action")) {
                ev.target.classList.add("dragging");
                Alpine.store("dragged", ev.target);
            }
        },

        dragEndHandler(ev) {
            if (ev.target instanceof Element && ev.target.classList.contains("action")) {
                ev.target.classList.remove("dragging");
                Alpine.store("dragged", undefined);
            }
        }
    }));

    Alpine.data('automation', () => ({
        action_list: [],
        start_url: "",
        errors: [],
        state: '',
        
        dragOverHandler(ev) {
            ev.preventDefault();
            if (ev.dataTransfer) {
                ev.dataTransfer.dropEffect = "copy";
            }
        },
        
        dropHandler(ev) {
            ev.preventDefault();
            let dropTarget = document.getElementById("target");
            let newAction = Alpine.store("dragged").cloneNode(true);
            // add a delete button which deletes the action from the list...
            let deleteButton = document.createElement("button");
            deleteButton.setAttribute('x-on:click.prevent', 'deleteAction($el)');
            deleteButton.appendChild(document.createTextNode("X"));
            newAction.appendChild(deleteButton);
            newAction.classList.remove("dragging");
            dropTarget.appendChild(newAction);
            this.action_list.push(newAction);
            let grabhandle = newAction.querySelector(".grabhandle");
            let title = grabhandle.querySelector("h3.title");
            newAction.insertBefore(title, grabhandle);
            newAction.removeChild(grabhandle);
            newAction.removeAttribute("draggable");
            console.debug(this.action_list);
        },

        clearList() {
            this.action_list = [];
            let targetHtml = document.getElementById("target");
            targetHtml.querySelectorAll("div.action:not(.gotopage-action)").forEach((div) => {
                targetHtml.removeChild(div);
            });
        },

        _checkUrlValid(input) {
            let url;
            try {
                url = new URL(input);
            } catch (_) {
                return false;
            }
            return true;
        },

        _markActionInvalid(htmlAction) {
            i
        },

        _clearValidation() {
            this.errors = [];
            startAction = document.querySelector("#starting-action input");
            startAction.classList.remove("invalid-input");
            startAction.classList.remove("animate-pulse");
            this.action_list.forEach((htmlAction) => {
                htmlAction.querySelectorAll("input").forEach((input) => {
                    input.classList.remove("invalid-input");
                    input.classList.remove("animate-pulse");
                })
            });
        },

        validate() {
            this._clearValidation();
            let valid = true;
            // check start URL is valid
            if (!this._checkUrlValid(this.start_url)) {
                startAction = document.querySelector("#starting-action input");
                startAction.classList.add("invalid-input");
                startAction.classList.add("animate-pulse");
                this.errors.push("Please enter a valid starting page URL.");
                valid = false;
            }
            // check there is at least 1 action
            if (this.action_list.length <= 0) {
                this.errors.push("Please add at least one action.");
                valid = false;
            }
            // check each action is valid
            let invalidInputs = false;
            this.action_list.forEach((htmlAction) => {
                htmlAction.querySelectorAll("input").forEach((input) => {
                    if (input.value.trim() === "") {
                        valid = false;
                        input.classList.add("invalid-input");
                        input.classList.add("animate-pulse");
                        invalidInputs = true;
                    }
                });
            });
            if (invalidInputs) {
                this.errors.push("Please make sure all actions are complete.");
            }
            console.log("Validate returning: ", valid);
            return valid;
        },

        closeInvalidDialog() {
            document.getElementById("invalidDialog").close();
        },

        _openInvalidDialog() {
            document.getElementById("invalidDialog").showModal();
        },

        _buildFinalActionList() {
            finalActionList = [];
            let action = {
                pw_action: "start",
                pw_url: this.start_url
            };
            finalActionList.push(action);
            this.action_list.forEach((htmlAction) => {
                let action = {};
                let pw_action = htmlAction._x_dataStack[0];
                let action_class = htmlAction.cloneNode(true).classList;
                action_class.remove("action");
                action.pw_action = action_class[0];
                action.pw_method = pw_action.pw_method;
                action.pw_method_arg = pw_action.pw_method_arg;
                action.pw_method_arg_2 = pw_action.pw_method_arg_2;
                finalActionList.push(action);
            });
            return finalActionList;
        },

        testAutomation() {
            if (!this.validate()) {
                this._openInvalidDialog();
                return;
            }
            this.state = 'Testing...';
            finalActions = this._buildFinalActionList();
            console.log(finalActions);
            // save, submit etc...
            // get form action for url, post finalActions as data to url...
            form_action = document.getElementById("submit_form").action;
            fetch(form_action, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(finalActions)
            })
            .then((stream) => {
                console.log("data submitted...");
                if (stream.ok) {
                    return stream.json();
                }
                throw new error("Response was not OK! Status: " + stream.status) 
            })
            .then((json) => {
                console.log(json);
                window.dispatchEvent(new CustomEvent("displayreport", {detail: json}));
                this.state='';
            })
            .catch((error) => {
                console.error(error);
            });
        }
    }));

    Alpine.data('report', () => ({
        data: false,
        show_report: false,

        displayReport(event) {
            this.data = event.detail;
            this.show_report = true;
            document.getElementById("video_element").load();
        },

        saveAutomation() {
            const queryString = window.location.search;
            const urlParams = new URLSearchParams(queryString);
            automation_name = urlParams.get("name");
            save_location = urlParams.get("save_location");
            data = {
                url: this.data["steps"][0]["url"],
                location: save_location,
                name: automation_name,
                supplier_id: Alpine.store('supplierId'),
                steps: this.data["steps"]
            };

            console.debug(data);

            fetch("/automations/" + data["supplier_id"] + "/save?supplier_name=" + encodeURIComponent(Alpine.store("supplierName")), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then((stream) => {
                console.log("data submitted...");
                if (stream.ok) {
                    return stream.json();
                }
                throw new error("Response was not OK! Status: " + stream.status) 
            })
            .then((json) => {
                console.log(json);
                window.location = json;
            })
            .catch((error) => {
                console.error(error);
            });
        }
    }));
});