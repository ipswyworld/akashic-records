import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as api from '../api';

export const useAnalytics = (userId = 'system_user') => {
  return useQuery({
    queryKey: ['analytics', userId],
    queryFn: () => api.fetchAnalytics(userId),
    refetchInterval: 30000, // Poll every 30s as before, but automated
  });
};

export const useArtifacts = (userId = 'system_user') => {
  return useQuery({
    queryKey: ['artifacts', userId],
    queryFn: () => api.fetchArtifacts(userId),
  });
};

export const usePsychology = (userId = 'system_user') => {
  return useQuery({
    queryKey: ['psychology', userId],
    queryFn: () => api.fetchPsychologyProfile(userId),
  });
};

export const useGraphTopology = (userId = 'system_user') => {
  return useQuery({
    queryKey: ['graphTopology', userId],
    queryFn: () => api.fetchGraphTopology(userId),
    refetchInterval: 10000,
  });
};

export const useActionHistory = (userId = 'system_user') => {
  return useQuery({
    queryKey: ['actionHistory', userId],
    queryFn: () => api.fetchActionHistory(userId),
  });
};

// Mutations
export const useUpdateSettings = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ settings, userId }) => api.updateUserSettings(settings, userId),
    onSuccess: (_, { userId }) => {
      queryClient.invalidateQueries({ queryKey: ['analytics', userId] });
      queryClient.invalidateQueries({ queryKey: ['psychology', userId] });
    },
  });
};

export const useIngestUrl = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ url, userId }) => api.ingestUrl(url, userId),
    onSuccess: (_, { userId }) => {
      queryClient.invalidateQueries({ queryKey: ['artifacts', userId] });
      queryClient.invalidateQueries({ queryKey: ['analytics', userId] });
    },
  });
};

export const useRunActionGoal = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ goal, userId }) => api.runActionGoal(goal, userId),
    onSuccess: (_, { userId }) => {
      queryClient.invalidateQueries({ queryKey: ['actionHistory', userId] });
    },
  });
};
