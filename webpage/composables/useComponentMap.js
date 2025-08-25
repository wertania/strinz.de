import { defineAsyncComponent } from "vue";

// Composable for managing component maps in content pages
export const useComponentMap = () => {
  // Import all general components
  const generalComponents = {
    Header: defineAsyncComponent(() =>
      import("~/components/general/Header.vue")
    ),
    Paragraph: defineAsyncComponent(() =>
      import("~/components/general/Paragraph.vue")
    ),
    Address: defineAsyncComponent(() =>
      import("~/components/general/Address.vue")
    ),
  };

  // Import all marketing components
  const marketingComponents = {
    FeatureSectionCenterAssigned: defineAsyncComponent(() =>
      import("~/components/marketing/FeatureSectionCenterAssigned.vue")
    ),
    CtaBanner: defineAsyncComponent(() =>
      import("~/components/marketing/CtaBanner.vue")
    ),
  };

  // Combine all component maps
  const componentMap = {
    ...generalComponents,
    ...marketingComponents,
  };

  return {
    componentMap,
  };
};
