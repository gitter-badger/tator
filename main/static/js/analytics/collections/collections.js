class AnalyticsCollections extends TatorPage {
    constructor() {
      super();

      //
      // Header
      //
      const header = document.createElement("div");
      this._headerDiv = this._header._shadow.querySelector("header");
      header.setAttribute("class", "annotation__header d-flex flex-items-center flex-justify-between px-6 f3");
      const user = this._header._shadow.querySelector("header-user");
      user.parentNode.insertBefore(header, user);

      const div = document.createElement("div");
      div.setAttribute("class", "d-flex flex-items-center");
      header.appendChild(div);

      this._breadcrumbs = document.createElement("analytics-breadcrumbs");
      div.appendChild(this._breadcrumbs);
      this._breadcrumbs.setAttribute("analytics-name", "Collections Gallery");

      // this._settings = document.createElement("analytics-settings");
      // this._settings.style.marginLeft = "50px";
      // div.appendChild(this._settings);

      // Wrapper to allow r.side bar to slide into left
      this.mainWrapper = document.createElement("div");
      this.mainWrapper.setAttribute("class", "analysis--main--wrapper col-12 d-flex");
      this._shadow.appendChild(this.mainWrapper);

      //
      // Define the main section of the page
      //
      this.main = document.createElement("main");
      this.main.setAttribute("class", "enitity-gallery--main col-12");
      this.mainWrapper.appendChild(this.main);

      //
      /* Slider w/ Cards Gallery */
      // Gallery of horizontal bars to view collections
      this._collectionsGallery = document.createElement("collections-gallery");
      this.main.appendChild(this._collectionsGallery);

      //
      /* Right Navigation Pane - Annotation Detail Viewer */
      this.aside = document.createElement("aside");
      this.aside.setAttribute("class", "entity-panel--container slide-close col-3")
      this.mainWrapper.appendChild(this.aside);

      // Gallery navigation panel
      this._panelContainer = document.createElement("entity-panel-container");
      this.aside.appendChild(this._panelContainer);

      //
      /* Other */
      // Class to hide and showing loading spinner
      // @TODO what is standard use?
      this.loading = new LoadingSpinner();
      this._shadow.appendChild(this.loading.getImg());

      // Modal parent - to pass to page components
      this.modal = document.createElement("modal-dialog");
      this._shadow.appendChild(this.modal);
      this.modal.addEventListener("open", this.showDimmer.bind(this));
      this.modal.addEventListener("close", this.hideDimmer.bind(this));

      // Note: this will show them if they exist, may be project by project
      this.acceptedTypes = ["Media", "Localization"]; // No Frame assoc not shown here
    }

  _init() {

    this.loading.showSpinner();
    this.showDimmer();

    // Initialize the settings with the URL. The settings will be used later on.
    //this._settings.processURL();

    // Database interface. This should only be used by the viewModel/interface code.
    this.projectId = Number(this.getAttribute("project-id"));
    this._modelData = new TatorData(this.projectId);
    this._modelData.collectionsInit(this.acceptedTypes).then(() => {

      // Card Data class collects raw model and parses into view-model format
      // this.slideData = document.createElement("collection-slide-data");
      // this.slideData.init(this._modelData);

      // this.cardData.addEventListener("setCardImage", (evt) => {
      //   this._filterResults.updateCardImage(evt.detail.id, evt.detail.image);
      // });

      // Init panel side behavior
      this._panelContainer.init({ main: this.main, aside: this.aside, pageModal: this.modal, modelData: this._modelData });

      // Update the card with the localization's associated media
      // this.cardData.addEventListener("setMedia", (evt) => {
      //   this._filterResults.updateCardMedia(evt.detail.id, evt.detail.media);
      // });

      // Pass panel and localization types to gallery
      this._collectionsGallery.init({
        panelContainer: this._panelContainer,
        pageModal: this.modal,
        modelData: this._modelData
      });

      // Init history & check if state is stored in URL, update default states
      //this.history = new FilterHistoryManagement({ _paginationState: this._paginationState, _filterState: this._filterState });
      //this._checkHistoryState();

      // Init Card Gallery and Right Panel
      // this._cardGallery({
      //   filterState: this._filterState,
      //   paginationState: this._paginationState
      // });

      // // Listen for pagination events
      // this._filterResults._paginator.addEventListener("selectPage", this._paginateFilterResults.bind(this));
      // this._filterResults._paginator_top.addEventListener("selectPage", this._paginateFilterResults.bind(this));

      // this._filterResults._paginator.setValues(this._paginationState);
      // this._filterResults._paginator_top.setValues(this._paginationState);

      // // Listen for filter events
      // this._filterView.addEventListener("filterParameters", this._updateFilterResults.bind(this));
      this.loading.hideSpinner();
      this.hideDimmer();

    });
  }

  attributeChangedCallback(name, oldValue, newValue) {
    TatorPage.prototype.attributeChangedCallback.call(this, name, oldValue, newValue);
    switch (name) {
      case "project-name":
        this._breadcrumbs.setAttribute("project-name", newValue);
        break;
      case "project-id":
        this._init();
        break;
    }
  }

  static get observedAttributes() {
    return ["project-name", "project-id"].concat(TatorPage.observedAttributes);
  }


  // Page dimmer handler
  showDimmer() {
    return this.setAttribute("has-open-modal", "");
  }

  hideDimmer() {
    return this.removeAttribute("has-open-modal");
  }
}
  
customElements.define("analytics-collections", AnalyticsCollections);