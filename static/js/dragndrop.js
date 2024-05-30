document.addEventListener('alpine:init', () => {
    
    Alpine.data('formelement', () => ({
        required: false,
        type: "",
        value: "",
        validation: "",

        constructor(r, t, v, validation) {
            this.required = r;
            this.type = t;
            this.value = v;
            this.validation = validation;
        }
    }));

    Alpine.data('validationresult', () => ({
        passed,
        form_els,

        create(p, els) {
            this.passed = p;
            if (els !== undefined && Array.isArray(els)) {
                this.form_els = els;
            } else if (els !== undefined) {
                this.form_els.push(els);
            }
        }
    }));

    Alpine.data('action', () => ({
        form_els,
        pw_method,
        pw_method_arg,

        constructor(htmlAction) {
            if (htmlAction) {
                this.populateFormElements(htmlAction);
                htmlAction.removeAttribute("draggable");
            }
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

        validate()  {
            let result = new ValidationResult(true);

            return result;
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


    Alpine.data('actionlist', () => ({
        actions,

        addAction(action) {
            this.actions.push(action);
        },

        removeAction(action) {
            let index = this.actions.indexOf(action);
            if (index > -1) this.actions.splice(index, 1);
        }
    }));

    Alpine.data('automation', () => ({
        action_list,

        constructor() {
            this.action_list = new ActionList();
            console.log("Automation created!");
        },
        
        dragOverHandler(ev) {
            ev.preventDefault();
            if (ev.dataTransfer) {
                ev.dataTransfer.dropEffect = "copy";
            }
        },
        
        dropHandler(ev) {
            ev.preventDefault();
            let dropTarget = document.getElementById("target");
            let newAction = (Alpine.store("dragged")).cloneNode(true);
            (newAction).classList.remove("dragging");
            dropTarget.appendChild(newAction);
            this.action_list.addAction(new Action(newAction));
            let grabhandle = (newAction).querySelector(".grabhandle");
            newAction.removeChild(grabhandle);
        },

        clearList() {

        }
    }));
});