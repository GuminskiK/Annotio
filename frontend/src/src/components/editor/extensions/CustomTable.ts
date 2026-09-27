import { Table } from '@tiptap/extension-table';

export const CustomTable = Table.extend({
  addAttributes() {
    return {
      ...this.parent?.(),
      align: {
        default: 'left',
        parseHTML: element => element.getAttribute('data-align') || 'left',
        renderHTML: attributes => {
          if (attributes.align === 'left') return {};
          return { 'data-align': attributes.align };
        },
      }
    };
  }
});
