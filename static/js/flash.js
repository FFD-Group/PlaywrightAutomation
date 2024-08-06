document.addEventListener('alpine:init', () => {

    Alpine.data('flash', () => ({
        message: '',

        loadMessage() {
            const queryString = window.location.search;
            const urlParams = new URLSearchParams(queryString);
            automation_id=urlParams.get("automation_id");
            supplier_name=urlParams.get("supplier_name");
            this.message = `Automation ID: ${automation_id} saved for ${supplier_name}.`;
            setTimeout(() => {
                this.message = '';
            }, 5000);
        }
    }));
});