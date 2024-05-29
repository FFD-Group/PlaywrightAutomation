
import Alpine from 'alpinejs'

window.Alpine = Alpine

class FormElement {
    required: Boolean;
    type: String;
    value: String;
    validation?: String;

    constructor(r: Boolean, t: String, v: String, validation?: String) {
        this.required = r;
        this.type = t;
        this.value = v;
        this.validation = validation;
    }
}

class ValidationResult {
    passed: Boolean;
    form_els: Array<FormElement> = [];

    constructor(p: Boolean, els?: Array<FormElement>|FormElement) {
        this.passed = p;
        if (els !== undefined && Array.isArray(els)) {
            this.form_els = els;
        } else if (els !== undefined) {
            this.form_els.push(els);
        }
    }
}

class Action {
    id: String = "0";
    form_els: Array<FormElement> = [];

    constructor(htmlAction?: HTMLDivElement) {
        if (htmlAction) {
            let el = document.getElementById(htmlAction.id);
            if (el) {
                this.id = el.id;
                let form = el.querySelector("form");
                // get each form element and add to form_els as a FormElement.
            }
        }
    }

    validate(): ValidationResult  {
        let result = new ValidationResult(true);

        return result;
    }

    dragStartHandler(ev: DragEvent) {
        if (ev.target instanceof Element && ev.target.classList.contains("action")) {
            ev.target.classList.add("dragging");
            Alpine.store("dragged", ev.target);
        }
    }

    dragEndHandler(ev: DragEvent) {
        if (ev.target instanceof Element && ev.target.classList.contains("action")) {
            ev.target.classList.remove("dragging");
            Alpine.store("dragged", undefined);
        }
    }
}

class ActionList {
    actions: Array<Action> = [];

    addAction(action: Action): undefined {
        this.actions.push(action);
    }

    removeAction(action: Action): undefined {
        let index = this.actions.indexOf(action);
        if (index > -1) this.actions.splice(index, 1);
    }
}

class Automation {
    action_list: ActionList;

    constructor() {
        this.action_list = new ActionList();
        console.log("Automation created!");
    }
    
    dragOverHandler(ev: DragEvent) {
        ev.preventDefault();
        if (ev.dataTransfer) {
            ev.dataTransfer.dropEffect = "copy";
        }
    }
    
    dropHandler(ev: DragEvent) {
        ev.preventDefault();
        let newAction = (Alpine.store("dragged") as Node).cloneNode(true);
        (newAction as Element).classList.remove("dragging");
        document.getElementById("target")!.appendChild(newAction);
        //this.action_list.addAction(newAction.$data)
        console.log("Dropped into the automation!");
    }

    clearList() {

    }
}

document.addEventListener('alpine:init', () => {
    Alpine.data('actionlist', () => {return new ActionList()});
    Alpine.data('automation', () => {return new Automation()});
    Alpine.data('action', () => {return new Action()});
    Alpine.store('dragged', undefined);
});

Alpine.start()