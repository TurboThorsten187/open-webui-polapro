export const polaproConfig = {
    // Wenn 'false' gesetzt, wird der 'Neuigkeiten' (Changelog) Bildschirm nach dem Laden nicht automatisch angezeigt
    showWhatsNewOnFirstLoad: false,
    
    // Wenn 'false' gesetzt, wird die Update-Benachrichtigung für Administratoren unten rechts nicht angezeigt
    showUpdateToast: false,

    // Wenn 'false' gesetzt, wird der Controls-Button rechts oben ausgeblendet
    showChatControlsButton: false,

    // Wenn 'false' gesetzt, wird der 'About' Tab in den Einstellungen ausgeblendet
    showAboutTab: false,

    // Wenn 'false' gesetzt, wird der 'Integrations' Tab in den Chat-Einstellungen ausgeblendet
    showChatIntegrationsTab: false,

    // Wenn 'false' gesetzt, wird die "Integrations"-Schaltfläche (das Plus/Zahnrad links neben der Chat-Eingabe) ausgeblendet
    showChatInputIntegrationsMenu: false,

    // Wenn 'false' gesetzt, wird im Plus-Menü beim Chat die Option zum Hochladen von Dateien ("Upload Files") ausgeblendet
    showChatInputMenuUploadFiles: false,

    // Wenn 'false' gesetzt, wird im Plus-Menü beim Chat die Option zur Aufnahme ("Capture") ausgeblendet
    showChatInputMenuCapture: false,

    // Wenn 'false' gesetzt, wird im Plus-Menü beim Chat die Option zum Anhängen einer Webseite ("Attach Webpage") ausgeblendet
    showChatInputMenuAttachWebpage: false,

    // Wenn 'false' gesetzt, wird der 'Personalization' (Personalisierung) Tab in den Chat-Einstellungen ausgeblendet
    showChatPersonalizationTab: false,

    // Wenn 'false' gesetzt, wird der initiale Begrüßungstext ("Explore the cosmos" etc.) vor der ersten Nachricht ausgeblendet
    showChatOnboarding: true,

    // --- Metadaten Feature ---
    // Hauptschalter für das Metadaten-Menü neben dem Plus-Button
    showMetadataMenu: true,
    
    // Einzelne Felder im Metadaten-Menü
    metadataFields: {
        firstName: true,
        lastName: true,
        party: true,
        role: true,
        electoralTerm: true,
        dateRange: true,
        speechId: true
    }
};
