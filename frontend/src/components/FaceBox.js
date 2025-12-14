import React from 'react';

/**
 * Componente per visualizzare un singolo riquadro volto
 * Memoizzato per evitare re-render inutili
 */
const FaceBox = ({ face, scaleX, scaleY, index }) => {
  const displayName = (face.fullName || face.name || "").toString().trim();
  const nameNormalized = displayName.toLowerCase();
  const isUnknown = !nameNormalized || nameNormalized.includes("sconosciuto") || nameNormalized === "unknown";
  
  const roleNormalized = (face.role || "").toString().trim().toLowerCase();
  
  let roleClass = "";
  if (isUnknown) {
    roleClass = "role-unknown";
  } else if (roleNormalized === "user") {
    roleClass = "role-user";
  } else if (roleNormalized === "guest") {
    roleClass = "role-guest";
  }

  return (
    <div
      key={index}
      className={`face-box ${isUnknown ? 'unknown' : ''} ${roleClass}`}
      style={{
        top: face.top * scaleY,
        left: face.left * scaleX,
        width: (face.right - face.left) * scaleX,
        height: (face.bottom - face.top) * scaleY,
      }}
    >
      <div className="face-label">
        {displayName || "UNKNOWN"}
        {typeof face.age === "number" && face.age > 0 && (
          <span className="face-age">, {face.age}</span>
        )}
      </div>

      {/* Relationship come etichetta tipo apice in basso, tranne per ruolo user */}
      {!isUnknown && roleNormalized !== "user" && face.relationship && (
        <div className="face-relationship">
          {face.relationship}
        </div>
      )}
    </div>
  );
};

// Memoizza il componente per evitare re-render quando non necessario
export default React.memo(FaceBox, (prevProps, nextProps) => {
  // Confronta props rilevanti per decidere se re-renderizzare
  return (
    prevProps.face.id === nextProps.face.id &&
    prevProps.face.name === nextProps.face.name &&
    prevProps.face.top === nextProps.face.top &&
    prevProps.face.left === nextProps.face.left &&
    prevProps.face.right === nextProps.face.right &&
    prevProps.face.bottom === nextProps.face.bottom &&
    prevProps.scaleX === nextProps.scaleX &&
    prevProps.scaleY === nextProps.scaleY
  );
});


