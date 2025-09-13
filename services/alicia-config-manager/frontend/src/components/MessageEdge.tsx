import { EdgeProps, getBezierPath } from 'reactflow';
import { memo } from 'react';

export const MessageEdge: React.FC<EdgeProps> = memo(({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
}) => {
  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  return (
    <>
      <path
        id={id}
        className="react-flow__edge-path"
        d={edgePath}
        stroke="#3b82f6"
        strokeWidth={2}
        fill="none"
      />
      {data?.messageCount && (
        <text>
          <textPath href={`#${id}`} style={{ fontSize: 12, fill: '#9ca3af' }}>
            {data.messageCount} messages
          </textPath>
        </text>
      )}
    </>
  );
});

MessageEdge.displayName = 'MessageEdge';
