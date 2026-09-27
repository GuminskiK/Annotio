import Image from '@tiptap/extension-image';
import { ReactNodeViewRenderer } from '@tiptap/react';
import { ImageNodeView } from './ImageNodeView';

export const CustomImage = Image.extend({
  addOptions() {
    return {
      ...this.parent?.(),
      inline: true,
    } as any; 
  },
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
      },
      width: {
        default: '100%',
        parseHTML: element => element.getAttribute('data-width') || '100%',
        renderHTML: attributes => {
          return { 'data-width': attributes.width, style: `width: ${attributes.width}` };
        }
      }
    };
  },
  addNodeView() {
    return ReactNodeViewRenderer(ImageNodeView);
  }
});
