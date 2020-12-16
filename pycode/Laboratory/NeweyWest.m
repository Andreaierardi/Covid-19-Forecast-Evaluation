function omegahat = NeweyWest(Z,nlags,bartlett)

% Returns the Newey-West estimator of the asymptotic variance matrix

% INPUTS
% Z         = nxk matrix 
% nlags     = number of lags
% bartlett  = 1 if bartlett kernel, 0 rectangular

% OUTPUTS: 
% omegahat  = Newey-West estimator of the covariance matrix

[T,~] = size(Z);

% de-mean the variables
Z = Z - ones(size(Z,1),1)*mean(Z);

% sample variance
samplevar = Z'*Z/T; 

omegahat = samplevar;

% sample autocovariances
if nlags > 0
   for ii = 1 : nlags
      gamma = (Z(1+ii:T,:)'*Z(1:T-ii,:) +Z(1:T-ii,:)'*Z(1+ii:T,:))/T;
      if bartlett
          weights = 1 - (ii/nlags);
      else
          weights = 1;
      end
      omegahat = omegahat + weights*gamma;
   end
end
