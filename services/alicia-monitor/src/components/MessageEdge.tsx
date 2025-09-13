import React from 'react';
import { EdgeProps, getSmoothStepPath } from 'reactflow';
import { animated, useSpring } from '@react-spring/web';

interface MessageEdgeData {
  messageCount?: number;
  lastMessage?: string;
  active?: boolean;
}

const MessageEdge: React.FC<EdgeProps<MessageEdgeData>> = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  style = {},
}) => {
  const [edgePath] = getSmoothStepPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
  });

  const isActive = data?.active || false;
  const messageCount = data?.messageCount || 0;

  // Animation for active edges
  const animatedProps = useSpring({
    stroke: isActive ? '#10B981' : '#6B7280',
    strokeWidth: isActive ? 4 : 2,
    strokeDasharray: isActive ? '8,4' : '4,2',
    config: { duration: 500 },
  });

  // Flowing particles animation
  const particleAnimation = useSpring({
    from: { offset: 0 },
    to: { offset: 1 },
    config: { duration: isActive ? 2000 : 0 },
    loop: isActive,
  });

  return (
    <>
      {/* Main edge line */}
      <animated.path
        id={id}
        style={{
          ...style,
          ...animatedProps,
        }}
        className="react-flow__edge-path"
        d={edgePath}
        markerEnd="url(#react-flow__arrowclosed)"
      />

      {/* Flowing particles for active edges */}
      {isActive && (
        <animated.circle
          r="3"
          fill="#10B981"
          style={{
            offsetPath: `path('${edgePath}')`,
            offsetDistance: particleAnimation.offset.to((value) => `${value * 100}%`),
          }}
        />
      )}

      {/* Message count label */}
      {messageCount > 0 && (
        <text
          dy={-5}
          style={{
            fontSize: '10px',
            fill: isActive ? '#10B981' : '#6B7280',
            fontWeight: 'bold',
            textAnchor: 'middle',
            pointerEvents: 'none',
            userSelect: 'none',
          }}
        >
          <textPath
            href={`#${id}`}
            startOffset="50%"
          >
            {messageCount > 99 ? '99+' : messageCount}
          </textPath>
        </text>
      )}
    </>
  );
};

export default MessageEdge;
