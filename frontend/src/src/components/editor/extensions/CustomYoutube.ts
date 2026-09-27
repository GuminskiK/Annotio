import Youtube from '@tiptap/extension-youtube';

export const CustomYoutube = Youtube.extend({
  addAttributes() {
    return {
      ...this.parent?.(),
      src: {
        default: null,
      },
      align: {
        default: 'left',
        parseHTML: element => element.getAttribute('data-align') || 'left',
        renderHTML: attributes => {
          if (attributes.align === 'left') return {};
          return { 'data-align': attributes.align };
        },
      },
      width: {
        default: '100%',
        parseHTML: element => element.getAttribute('data-width') || '100%',
        renderHTML: attributes => {
          return { 'data-width': attributes.width, style: `width: ${attributes.width}` };
        }
      }
    };
  }
});
