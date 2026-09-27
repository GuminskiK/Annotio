import { Node, mergeAttributes } from '@tiptap/core';
import { ReactNodeViewRenderer, NodeViewWrapper } from '@tiptap/react';

export const NoteLink = Node.create({
  name: 'noteLink',
  group: 'inline',
  inline: true,
  selectable: true,
  atom: true,

  addAttributes() {
    return {
      noteId: { default: null },
      title: { default: 'Unknown Note' },
    };
  },

  parseHTML() {
    return [
      {
        tag: 'span[data-type="note-link"]',
      },
    ];
  },

  renderHTML({ HTMLAttributes }) {
    return ['span', mergeAttributes(HTMLAttributes, { 'data-type': 'note-link', class: 'text-blue-600 bg-blue-50 px-1 py-0.5 rounded cursor-pointer hover:bg-blue-100 transition-colors' }), `@${HTMLAttributes.title}`];
  },

  addNodeView() {
    return ReactNodeViewRenderer((props) => {
      return (
        <NodeViewWrapper as="span" className="inline-block">
          <span 
            className="text-blue-600 bg-blue-50 px-1 py-0.5 rounded cursor-pointer hover:bg-blue-100 transition-colors"
            onClick={() => alert(`Redirect to note: ${props.node.attrs.noteId}`)}
          >
            📄 {props.node.attrs.title}
          </span>
        </NodeViewWrapper>
      );
    });
  },
});
