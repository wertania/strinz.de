const G_TAG = "G-BQZP7Z00PV";

// Cookie functions
declare global {
  interface Window {
    dataLayer: any[];
  }
}

export const useCookieConsent = () => {
  const setCookie = (name: string, value: string, days: number) => {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
  };

  const getCookie = (name: string): string | null => {
    const nameEQ = name + "=";
    const ca = document.cookie.split(";");
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === " ") c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
  };

  // Initialize Google Analytics
  const initializeGoogleAnalytics = () => {
    const googleAnalytics = useScriptGoogleAnalytics({
      id: G_TAG,
    });
    console.log("GoogleAnalytics is initialized");
  };

  return {
    setCookie,
    getCookie,
    initializeGoogleAnalytics,
  };
};
